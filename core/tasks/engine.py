"""
TaskEngine -- Gera e gerencia tarefas praticas de operacao Shopee.

Em vez de XP/missoes abstratas (gamificacao antiga), este engine cria
tarefas acionaveis baseadas no estado real dos dados:
  - Upload de vendas atrasado
  - Estoque baixo
  - Dados de concorrencia desatualizados
  - Fim de mes (relatorio pendente)
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select, func
from core.database.models import Task, Transaction, InventoryItem, CompetitorListing, Product


class TaskEngine:
    """Engine that scans DB state and generates/updates practical tasks."""

    @staticmethod
    def scan_and_generate(session: Session, user_id: int) -> List[Task]:
        """Run all checks and return newly created tasks."""
        new_tasks: List[Task] = []
        new_tasks.extend(TaskEngine._check_sales_upload(session, user_id))
        new_tasks.extend(TaskEngine._check_inventory(session, user_id))
        new_tasks.extend(TaskEngine._check_competitors(session, user_id))
        new_tasks.extend(TaskEngine._check_end_of_month(session, user_id))
        if new_tasks:
            for t in new_tasks:
                session.add(t)
            session.commit()
        return new_tasks

    @staticmethod
    def get_pending(session: Session, user_id: int) -> List[Task]:
        """Return incomplete tasks sorted by priority (1 first)."""
        stmt = (
            select(Task)
            .where(Task.user_id == user_id, Task.is_completed == False)
            .order_by(Task.priority, Task.created_at.desc())
        )
        return list(session.exec(stmt).all())

    @staticmethod
    def get_completed(session: Session, user_id: int, limit: int = 20) -> List[Task]:
        """Return most recently completed tasks."""
        stmt = (
            select(Task)
            .where(Task.user_id == user_id, Task.is_completed == True)
            .order_by(Task.completed_at.desc())
            .limit(limit)
        )
        return list(session.exec(stmt).all())

    @staticmethod
    def complete(session: Session, task_id: int) -> Optional[Task]:
        """Mark a task as completed."""
        task = session.get(Task, task_id)
        if task and not task.is_completed:
            task.is_completed = True
            task.completed_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def count_pending(session: Session, user_id: int) -> int:
        """Return number of pending tasks."""
        result = session.exec(
            select(func.count(Task.id))
            .where(Task.user_id == user_id, Task.is_completed == False)
        ).one()
        return result or 0

    @staticmethod
    def _task_exists(session: Session, user_id: int, title_contains: str) -> bool:
        """Check if a pending task with similar title already exists."""
        stmt = (
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.is_completed == False,
                Task.title.like(f"%{title_contains}%"),
            )
        )
        return session.exec(stmt).first() is not None

    @staticmethod
    def _check_sales_upload(session: Session, user_id: int) -> List[Task]:
        """Check if last upload was > 7 days ago."""
        last_date = session.exec(
            select(func.max(Transaction.date))
            .where(Transaction.user_id == user_id)
        ).one()
        if last_date is None:
            if not TaskEngine._task_exists(session, user_id, "Upload"):
                return [Task(
                    title="\U0001f4e4 Primeiro upload de vendas",
                    description="Nenhuma venda registrada. Faca upload da planilha do Seller Center.",
                    category="vendas", priority=1, target_tab="financeiro", user_id=user_id,
                )]
            return []
        days_since = (datetime.utcnow() - last_date).days
        if days_since >= 7:
            if not TaskEngine._task_exists(session, user_id, "Upload"):
                return [Task(
                    title="\U0001f4e4 Upload de vendas pendente",
                    description=f"Ultimo upload ha **{days_since} dias**. Faca upload da planilha mais recente.",
                    category="vendas", priority=2, target_tab="financeiro", user_id=user_id,
                )]
        return []

    @staticmethod
    def _check_inventory(session: Session, user_id: int) -> List[Task]:
        """Check for items below minimum stock."""
        stmt = select(InventoryItem).where(
            InventoryItem.user_id == user_id,
            InventoryItem.stock < InventoryItem.min_stock,
        )
        new_tasks = []
        for item in session.exec(stmt).all():
            if not TaskEngine._task_exists(session, user_id, item.name[:30]):
                urgency = 2 if item.stock <= item.min_stock // 2 else 3
                new_tasks.append(Task(
                    title=f"\U0001f4e6 Repor estoque: {item.name}",
                    description=f"**Estoque atual:** {item.stock} un. | **Minimo:** {item.min_stock} un.",
                    category="estoque", priority=urgency, target_tab="anuncios", user_id=user_id,
                ))
        return new_tasks

    @staticmethod
    def _check_competitors(session: Session, user_id: int) -> List[Task]:
        """Check for products without recent competitor data."""
        products = list(session.exec(
            select(Product).where(Product.user_id == user_id)
        ).all())
        five_days_ago = datetime.utcnow() - timedelta(days=5)
        new_tasks = []
        for product in products:
            latest_check = session.exec(
                select(func.max(CompetitorListing.last_checked_at))
                .where(CompetitorListing.product_id == product.id)
            ).one()
            short = product.title[:50]
            if latest_check is None:
                if not TaskEngine._task_exists(session, user_id, "Concorrencia"):
                    new_tasks.append(Task(
                        title=f"\U0001f50d Concorrencia: {short}",
                        description="Produto sem dados de concorrencia. Faca a primeira varredura de precos.",
                        category="concorrencia", priority=1, target_tab="concorrencia", user_id=user_id,
                    ))
            elif latest_check < five_days_ago:
                if not TaskEngine._task_exists(session, user_id, "Atualizar concorrencia"):
                    days_stale = (datetime.utcnow() - latest_check).days
                    new_tasks.append(Task(
                        title=f"\U0001f50d Atualizar concorrencia: {short}",
                        description=f"Dados desatualizados ha **{days_stale} dias**. Verifique os precos.",
                        category="concorrencia", priority=3, target_tab="concorrencia", user_id=user_id,
                    ))
        return new_tasks

    @staticmethod
    def _check_end_of_month(session: Session, user_id: int) -> List[Task]:
        """Check if month-end report is needed."""
        now = datetime.utcnow()
        if now.day < 26:
            return []
        if TaskEngine._task_exists(session, user_id, "Relatorio Mensal"):
            return []
        return [Task(
            title="\U0001f4ca Relatorio mensal pendente",
            description=f"Fim de mes chegando ({now.day}/{(now.month % 12) + 1}). Gere o relatorio mensal.",
            category="relatorio", priority=3, target_tab="resumo", user_id=user_id,
        )]
