from agents.base_agent import BaseAgent
from core.llm_client import llm_client
from core.database.engine import get_session
from core.database.models import Transaction, User
from sqlmodel import select, Session
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime

class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Finance Guardian")

    def process_upload(self, file, user_id: int) -> dict:
        """
        Parses a Shopee Sales Report (CSV/XLSX) and saves transactions.
        Simple mapper for now: expects columns like 'Data', 'Valor', 'Descrição'.
        """
        try:
            # Detect file type
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Simple Column Normalization (Mocking Shopee standard columns)
            # Shopee usually has: 'Data do Pedido', 'Valor Total', 'Nome do Produto'
            # We will look for these or fallback to generic english
            
            # TODO: Add robust column mapping logic
            # For MVP, we assume the user uploads a clean template or we map loosely
            
            date_col = next((c for c in df.columns if 'date' in c.lower() or 'data' in c.lower()), None)
            amount_col = next((c for c in df.columns if 'amount' in c.lower() or 'valor' in c.lower() or 'total' in c.lower()), None)
            desc_col = next((c for c in df.columns if 'item' in c.lower() or 'prod' in c.lower() or 'desc' in c.lower()), 'Item Generico')

            if not date_col or not amount_col:
                return {"success": False, "message": "Colunas 'Data' ou 'Valor' não encontradas."}

            session = next(get_session())
            count = 0
            
            for _, row in df.iterrows():
                try:
                    # Clean Amount
                    val_str = str(row[amount_col]).replace('R$', '').replace(',', '.').strip()
                    amount = float(val_str)
                    
                    # Clean Date
                    date_val = pd.to_datetime(row[date_col])

                    txn = Transaction(
                        date=date_val,
                        type="INCOME", # Assuming sales report for now
                        category="Sale",
                        description=str(row.get(desc_col, "Venda Shopee")),
                        amount=amount,
                        user_id=user_id
                    )
                    session.add(txn)
                    count += 1
                except Exception as e:
                    print(f"Skipping row: {e}")
                    continue
            
            session.commit()
            return {"success": True, "message": f"{count} transações importadas com sucesso!"}

        except Exception as e:
            return {"success": False, "message": f"Erro ao processar arquivo: {str(e)}"}

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



    def add_transaction(self, date: datetime, description: str, amount: float, category: str, type: str, user_id: int):
        """Manually adds a single transaction."""
        try:
            session = next(get_session())
            txn = Transaction(
                date=date,
                description=description,
                amount=amount,
                category=category,
                type=type,
                user_id=user_id
            )
            session.add(txn)
            session.commit()
            return {"success": True, "message": "Transação registrada com sucesso!"}
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
                return {"success": True, "message": "Transação removida."}
            return {"success": False, "message": "Transação não encontrada."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao deletar: {str(e)}"}

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
                return {"success": True, "message": "Transação atualizada."}
            return {"success": False, "message": "Transação não encontrada."}
        except Exception as e:
            return {"success": False, "message": f"Erro ao atualizar: {str(e)}"}

    def generate_deep_analysis(self, user_id: int) -> str:
        """Generates a comprehensive financial report using LLM."""
        stats = self.get_financial_stats(user_id)
        if stats["transaction_count"] == 0:
            return "Sem dados suficientes para análise profunda. Por favor, registre vendas ou despesas."

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
        
        # Construct Context
        context = f"""
        FATURAMENTO TOTAL: R$ {stats['total_revenue']:.2f}
        CUSTOS TOTAIS: R$ {stats['total_expenses']:.2f}
        LUCRO LÍQUIDO: R$ {stats['net_profit']:.2f}
        MARGEM DE LUCRO: {stats['margin']:.2f}%
        
        TOP 3 PRODUTOS (Mais Vendidos):
        {', '.join([f'{p[0]} (R$ {p[1]:.2f})' for p in top_selling])}
        
        BOTTOM 3 PRODUTOS (Menos Vendidos):
        {', '.join([f'{p[0]} (R$ {p[1]:.2f})' for p in least_selling])}
        """
        
        prompt = f"""
        Atue como um CFO (Diretor Financeiro) experiente de E-commerce. Analise os dados abaixo da loja "Shopee Growth Quest":
        
        {context}
        
        Gere um relatório estruturado em Markdown com:
        1. 🏆 **O que está funcionando?** (Destaque pontos fortes e Top Produtos)
        2. ⚠️ **Pontos de Atenção** (Análise de custos e margem. Se a margem for baixo de 20%, critique. Se custos > 40% da receita, alerte).
        3. 💡 **Oportunidades de Melhoria** (Sugestões para os produtos menos vendidos: Bundle? Promoção? Ads? Descontinuar?).
        4. 🚀 **Plano de Ação** (3 passos práticos para aumentar o lucro na próxima semana).
        
        Seja direto, profissional mas motivador. Use emojis para facilitar a leitura.
        """
        
        return llm_client.generate_content(prompt)



    def run(self, user_id: int):
        """Default run method required by BaseAgent."""
        return self.analyze_health(user_id)
