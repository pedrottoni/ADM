from agents.base_agent import BaseAgent
from core.llm_client import llm_client
import pandas as pd
from typing import Dict, Any

class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("Finance Guardian")

    def analyze_sales(self, sales_data: list[Dict[str, Any]]):
        """
        Analyzes a list of sales transactions.
        Data format: [{'date': '2023-10-01', 'amount': 100.0, 'items': 'Shirt'}, ...]
        """
        if not sales_data:
            return "Nenhuma venda registrada ainda. O reino está silencioso..."

        # Convert to DataFrame for easier math
        df = pd.DataFrame(sales_data)
        total_revenue = df['amount'].sum()
        transaction_count = len(df)
        avg_ticket = total_revenue / transaction_count

        summary_stats = f"""
        Total Revenue: R$ {total_revenue:.2f}
        Transactions: {transaction_count}
        Avg Ticket: R$ {avg_ticket:.2f}
        """
        self.log(f"Stats calculated: {summary_stats}")

        # Ask AI for "Coach" advice
        prompt = f"""
        Você é o Guardião Financeiro de uma loja na Shopee.
        Aqui estão os dados recentes:
        {summary_stats}
        
        Dê um conselho curto, motivacional e gamificado (estilo RPG) para o dono da loja sobre como aumentar o lucro.
        Máximo de 2 frases.
        """
        advice = llm_client.generate_content(prompt)
        return {"stats": summary_stats, "advice": advice}

    def run(self, data):
        return self.analyze_sales(data)
