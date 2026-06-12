from agents.base_agent import BaseAgent
from core.llm_client import llm_client
from core.database.engine import get_session
from core.database.models import Transaction, User, Product, ProductComponent, InventoryItem
from core.sales_service import SalesService
from sqlmodel import select, Session
from sqlalchemy.orm import selectinload
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Finance Guardian")
        self.sales_service = SalesService()

    def process_upload(self, file, user_id: int) -> dict:
        """
        Phase 1: Reads a CSV/XLSX file and sends it to the LLM for intelligent parsing.
        Returns structured data for preview (does NOT save yet).
        """
        try:
            # Read file content
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Convert to string for LLM (limit to 100 rows to avoid token overflow)
            csv_text = df.head(100).to_csv(index=False)
            total_rows = len(df)
            
            # Build LLM prompt
            prompt = f"""Você é um assistente especializado em processar relatórios de vendas de e-commerce.

Analise este arquivo de vendas e extraia as informações relevantes em formato JSON.

ARQUIVO (primeiras {min(total_rows, 100)} de {total_rows} linhas):
```
{csv_text}
```

REGRAS:
1. Extraia APENAS pedidos com status "Concluído", "Completo", "Completed", "Delivered" ou similar. IGNORE pedidos "Cancelado", "Cancelled", "Devolvido", "Returned".
2. Identifique as colunas corretas para: data do pedido, nome do produto, valor total da venda.
3. Se houver uma coluna de quantidade, use-a. Caso contrário, assuma quantidade = 1.
4. Se houver taxas/frete como colunas separadas, NÃO inclua como valor da venda.
5. Limpe valores monetários (remova "R$", converta vírgula para ponto).

RETORNE ESTRITAMENTE um JSON array com este formato (sem markdown, sem explicação, APENAS o JSON):
[
  {{"date": "2025-01-01", "product": "Nome do Produto", "amount": 89.90, "quantity": 1, "status": "Concluído"}},
  ...
]

Se o arquivo estiver vazio ou não contiver vendas válidas, retorne: []"""

            # Call LLM
            response = llm_client.generate_content(prompt)
            
            # Parse JSON from LLM response
            parsed_data = self._extract_json_from_response(response)
            
            if parsed_data is None:
                return {"success": False, "message": "Não foi possível interpretar o arquivo. Verifique o formato.", "raw_response": response}
            
            return {
                "success": True, 
                "data": parsed_data,
                "total_rows_in_file": total_rows,
                "parsed_count": len(parsed_data),
                "message": f"LLM extraiu {len(parsed_data)} vendas válidas de {total_rows} linhas."
            }

        except Exception as e:
            return {"success": False, "message": f"Erro ao processar arquivo: {str(e)}"}

    def confirm_upload(self, sales_data: List[Dict], user_id: int) -> dict:
        """
        Phase 2: After user reviews the preview, save transactions and update stock.
        Delegates to SalesService for stock management.
        """
        try:
            result = self.sales_service.process_income_batch(sales_data, user_id)
            return result
        except Exception as e:
            return {"success": False, "message": f"Erro ao confirmar upload: {str(e)}"}

    def _extract_json_from_response(self, response: str):
        """Extract JSON array from LLM response, handling markdown code blocks."""
        try:
            # Try direct parse first
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code block
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Try finding array brackets
        bracket_match = re.search(r'\[.*\]', response, re.DOTALL)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None

    def get_financial_stats(self, user_id: int) -> Dict[str, Any]:
        """Calculates Revenue, Costs, Profit from DB."""
        session = next(get_session())
        statement = select(Transaction).where(Transaction.user_id == user_id)
        transactions = session.exec(statement).all()
        
        total_revenue = sum(t.amount for t in transactions if t.type == "INCOME")
        total_expenses = sum(t.amount for t in transactions if t.type == "EXPENSE")
        profit = total_revenue - total_expenses
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_profit": profit,
            "margin": margin,
            "transaction_count": len(transactions),
            "raw_data": transactions # Useful for displaying table
        }

    def analyze_health(self, user_id: int):
        stats = self.get_financial_stats(user_id)
        
        if stats["transaction_count"] == 0:
            return {"stats": stats, "advice": "O cofre está vazio. Suba suas vendas para que eu possa analisar!"}

        summary_text = f"""
        Revenue: R$ {stats['total_revenue']:.2f}
        Costs: R$ {stats['total_expenses']:.2f}
        Profit: R$ {stats['net_profit']:.2f}
        Margin: {stats['margin']:.2f}%
        """
        
        prompt = f"""
        Você é o Guardião Financeiro (RPG Fantasy Style).
        Dados da Loja:
        {summary_text}
        
        Dê um conselho tático (1 frase) e uma frase motivacional curta.
        Se a margem for baixa (<10%), alerte o usuário.
        """
        
        advice = llm_client.generate_content(prompt)
        return {"stats": stats, "advice": advice}

    def add_transaction(self, date: datetime, description: str, amount: float, 
                       category: str, type: str, user_id: int, 
                       product_id: int = None, quantity: int = 1):
        """
        Manually adds a single transaction.
        If type is INCOME and product_id is provided, also updates stock.
        """
        try:
            session = next(get_session())
            
            txn = Transaction(
                date=date,
                description=description,
                amount=amount,
                category=category,
                type=type,
                product_id=product_id,
                quantity=quantity,
                user_id=user_id
            )
            session.add(txn)
            
            stock_result = None
            
            # If it's a sale with a linked product, update stock
            if type == "INCOME" and product_id:
                product = session.get(Product, product_id)
                if product:
                    stock_result = self.sales_service.process_sale(product, quantity, session)
            
            session.commit()
            
            return {
                "success": True, 
                "message": "Transacao registrada com sucesso!",
                "stock_updated": stock_result is not None,
                "stock_result": stock_result
            }
        except Exception as e:
            return {"success": False, "message": f"Erro ao registrar: {str(e)}"}

    def delete_transaction(self, transaction_id: int):
        """Deletes a transaction by ID."""
        try:
            session = next(get_session())
            txn = session.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
            if txn:
                session.delete(txn)
                session.commit()
                return {"success": True, "message": "Transacao removida."}
            return {"success": False, "message": "Transacao nao encontrada."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar: {str(e)}"}

    def clear_all_transactions(self, user_id: int):
        """Removes all transactions for the user."""
        try:
            session = next(get_session())
            statement = select(Transaction).where(Transaction.user_id == user_id)
            transactions = session.exec(statement).all()
            for t in transactions:
                session.delete(t)
            session.commit()
            return {"success": True, "message": "Historico financeiro zerado!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao zerar: {str(e)}"}

    def reset_inventory(self, user_id: int, initial_stock: int = 600):
        """Resets all inventory items to a fixed initial stock."""
        try:
            from core.database.models import InventoryItem
            session = next(get_session())
            statement = select(InventoryItem).where(InventoryItem.user_id == user_id)
            items = session.exec(statement).all()
            for item in items:
                item.stock = initial_stock
                session.add(item)
            session.commit()
            return {"success": True, "message": f"Estoque fisico resetado para {initial_stock} unidades!"}
        except Exception as e:
            return {"success": False, "message": f"Erro ao resetar estoque: {str(e)}"}

    def update_transaction(self, transaction_id: int, updates: Dict[str, Any]):
        """Updates a transaction."""
        try:
            session = next(get_session())
            txn = session.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
            if txn:
                for key, value in updates.items():
                    setattr(txn, key, value)
                session.add(txn)
                session.commit()
                return {"success": True, "message": "Transacao atualizada."}
            return {"success": False, "message": "Transacao nao encontrada."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar: {str(e)}"}

    def generate_deep_analysis(self, user_id: int, context_cogs: dict = None) -> str:
        """Generates a comprehensive financial report using LLM."""
        stats = self.get_financial_stats(user_id)
        if stats["transaction_count"] == 0:
            return "Sem dados suficientes para analise profunda. Por favor, registre vendas ou despesas."

        # Aggregate Product Sales
        transactions = stats["raw_data"]
        sales_data = {} # {description: amount}
        for t in transactions:
            if t.type == "INCOME" and t.description:
                sales_data[t.description] = sales_data.get(t.description, 0) + t.amount

        # Sort Top/Bottom
        sorted_sales = sorted(sales_data.items(), key=lambda x: x[1], reverse=True)
        top_selling = sorted_sales[:3]
        least_selling = sorted_sales[-3:] if len(sorted_sales) > 3 else []

        # Usar COGS real se fornecido, senao usar o calculado simples
        if context_cogs:
            fat_bruto = context_cogs.get('fat_bruto', stats['total_revenue'])
            saidas = context_cogs.get('saidas', stats['total_expenses'])
            cogs = context_cogs.get('cogs', 0)
            lucro_real = context_cogs.get('lucro_real', stats['net_profit'])
            margem_real = context_cogs.get('margem_real', stats['margin'])
        else:
            fat_bruto = stats['total_revenue']
            saidas = stats['total_expenses']
            cogs = 0
            lucro_real = stats['net_profit']
            margem_real = stats['margin']

        # Construct Context
        context = f"""
        FATURAMENTO BRUTO: R$ {fat_bruto:.2f}
        SAÍDAS (Despesas/Ads): R$ {saidas:.2f}
        COGS (Custo dos Produtos Vendidos): R$ {cogs:.2f}
        LUCRO REAL: R$ {lucro_real:.2f}
        MARGEM REAL: {margem_real:.2f}%

        TOP 3 PRODUTOS (Mais Vendidos):
        {', '.join([f'{p[0]} (R$ {p[1]:.2f})' for p in top_selling])}

        BOTTOM 3 PRODUTOS (Menos Vendidos):
        {', '.join([f'{p[0]} (R$ {p[1]:.2f})' for p in least_selling])}
        """
        
        prompt = f"""
        Atue como um CFO (Diretor Financeiro) experiente de E-commerce. Analise os dados abaixo da loja "Shopee Growth Quest":
        
        {context}
        
        Gere um relatório estruturado em Markdown com:
        1. **O que está funcionando?** (Destaque pontos fortes e Top Produtos)
        2. **Pontos de Atenção** (Análise de custos e margem. Se a margem for baixo de 20%, critique. Se custos > 40% da receita, alerte).
        3. **Oportunidades de Melhoria** (Sugestões para os produtos menos vendidos: Bundle? Promoção? Ads? Descontinuar?).
        4. **Plano de Ação** (3 passos práticos para aumentar o lucro na próxima semana).
        
        Seja direto, profissional mas motivador. Use emojis para facilitar a leitura.
        """
        
        return llm_client.generate_content(prompt)

    def calculate_order_profit(
        self,
        gross_revenue: float,
        product_cost: float,
        quantity: int = 1,
        discount: float = 0.0,
        shopee_fee_pct: float = 18.0,
        shopee_fixed_fee: float = 5.0,
        ads_pct: float = 15.0,
        tax_pct: float = 6.0,
        extra_costs: float = 0.0
    ) -> Dict[str, Any]:
        """
        Centralized per-order profit calculation.
        Calculates net profit after all Shopee fees, taxes, ads, product costs.
        Replaces the duplicated calculator logic in dashboard/main.py.
        
        Returns a dict with all line items for display or further use.
        """
        net_revenue_base = gross_revenue - discount

        comissao_shopee = net_revenue_base * (shopee_fee_pct / 100.0)
        taxa_fixa = min(shopee_fixed_fee * quantity, 100.0)
        custo_ads = net_revenue_base * (ads_pct / 100.0)
        custo_imposto = net_revenue_base * (tax_pct / 100.0)
        custo_produto = product_cost * quantity

        total_deductions = discount + comissao_shopee + taxa_fixa + custo_ads + custo_imposto + custo_produto + extra_costs
        net_profit = gross_revenue - total_deductions
        profit_margin = (net_profit / gross_revenue * 100.0) if gross_revenue > 0 else 0.0

        return {
            "gross_revenue": gross_revenue,
            "net_revenue_base": net_revenue_base,
            "discount": discount,
            "shopee_commission": comissao_shopee,
            "shopee_fixed_fee": taxa_fixa,
            "ads_cost": custo_ads,
            "tax_cost": custo_imposto,
            "product_cost": custo_produto,
            "extra_costs": extra_costs,
            "total_deductions": total_deductions,
            "net_profit": net_profit,
            "profit_margin": profit_margin,
            "roi": (net_profit / custo_produto * 100.0) if custo_produto > 0 else 0.0
        }

    def get_top_products(self, user_id: int, limit: int = 5,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Returns top-selling products by revenue from transactions.
        Optionally filtered by date range (inclusive)."""
        session = next(get_session())
        filters = [
            Transaction.user_id == user_id,
            Transaction.type == "INCOME",
            Transaction.product_id.isnot(None)
        ]
        if start_date and end_date:
            filters.append(Transaction.date.between(start_date, end_date))
        statement = select(Transaction).where(*filters).order_by(Transaction.amount.desc())
        transactions = session.exec(statement).all()

        product_sales: Dict[int, Dict] = {}
        for t in transactions:
            pid = t.product_id
            if pid not in product_sales:
                product_sales[pid] = {
                    "product_id": pid,
                    "product_title": t.description,
                    "total_revenue": 0.0,
                    "total_quantity": 0,
                    "transaction_count": 0
                }
            product_sales[pid]["total_revenue"] += t.amount
            product_sales[pid]["total_quantity"] += t.quantity or 1
            product_sales[pid]["transaction_count"] += 1

        # Fetch product titles for proper names
        sorted_products = sorted(product_sales.values(), key=lambda x: x["total_revenue"], reverse=True)
        for p in sorted_products:
            prod = session.get(Product, p["product_id"])
            if prod:
                p["product_title"] = prod.title

        return sorted_products[:limit]

    def get_top_products_by_potes(self, user_id: int, limit: int = 10,
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Returns top products grouped by base name, ranked by potes sold.
        Optionally filtered by date range (inclusive)."""
        session = next(get_session())
        filters = [
            Transaction.user_id == user_id,
            Transaction.type == "INCOME",
            Transaction.product_id.isnot(None)
        ]
        if start_date and end_date:
            filters.append(Transaction.date.between(start_date, end_date))
        transactions = session.exec(select(Transaction).where(*filters)).all()

        kits_por_produto: Dict[int, int] = {}
        for t in transactions:
            pid = t.product_id
            kits_por_produto[pid] = kits_por_produto.get(pid, 0) + (t.quantity or 1)

        produtos = session.exec(
            select(Product).options(selectinload(Product.components)).where(Product.user_id == user_id)
        ).all()

        inventory_items = session.exec(
            select(InventoryItem).where(InventoryItem.user_id == user_id)
        ).all()

        grupos: Dict[str, int] = {}
        for p in produtos:
            kits = kits_por_produto.get(p.id, 0)
            if kits == 0:
                continue

            base_name = re.sub(r' - \d+x$', '', p.title.strip()).strip()

            potes = 0
            if hasattr(p, 'components') and p.components:
                for comp in p.components:
                    inv_item = next((i for i in inventory_items if i.id == comp.inventory_item_id), None)
                    if inv_item:
                        potes += kits * (comp.quantity or 1)
            else:
                potes = kits

            grupos[base_name] = grupos.get(base_name, 0) + potes

        result = sorted(grupos.items(), key=lambda x: x[1], reverse=True)
        session.close()
        return [
            {"product_title": name, "total_potes": potes}
            for name, potes in result[:limit]
        ]

    def run(self, user_id: int):
        """Default run method required by BaseAgent."""
        return self.analyze_health(user_id)
