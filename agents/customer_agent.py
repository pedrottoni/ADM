from agents.base_agent import BaseAgent
from core.llm_client import llm_client
from typing import List, Dict

class CustomerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Customer Hero")

    def generate_response(self, customer_message: str, tone: str = "Empático") -> str:
        """Generates a reply to a customer message."""
        prompt = f"""
        Você é um atendente de suporte da Shopee nota 10.
        Responda à seguinte mensagem de um cliente:
        "{customer_message}"
        
        Tom de voz: {tone}.
        Regras: Seja breve, resolutivo e nunca prometa o que não pode cumprir.
        """
        return llm_client.generate_content(prompt)

    def analyze_sentiment(self, reviews: List[str]) -> Dict[str, any]:
        """Analyzes sentiment of multiple reviews."""
        if not reviews:
            return {"sentiment": "Sem dados", "summary": "Nenhuma avaliação para analisar."}
            
        reviews_text = "\n".join([f"- {r}" for r in reviews])
        prompt = f"""
        Analise estas avaliações da minha loja:
        {reviews_text}
        
        1. Classifique o sentimento geral (Positivo, Neutro, Negativo).
        2. Liste os 3 principais pontos de reclamação (se houver).
        3. Liste os 3 principais elogios.
        
        Retorne em formato de resumo tático.
        """
        analysis = llm_client.generate_content(prompt)
        return {"analysis": analysis}

    def run(self, *args, **kwargs):
        pass
