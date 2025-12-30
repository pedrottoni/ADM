from agents.base_agent import BaseAgent
from core.llm_client import llm_client
from typing import Dict, Any, List

class AdsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Ads Master")

    def generate_keywords(self, product_name: str, category: str) -> List[str]:
        """Generate keyword suggestions using LLM."""
        prompt = f"""
        Atue como um Especialista em Shopee Ads.
        Gere uma lista de 10 palavras-chave de alta conversão para o seguinte produto:
        Produto: {product_name}
        Categoria: {category}
        
        Retorne APENAS a lista simples, separada por vírgulas.
        """
        response = llm_client.generate_content(prompt)
        # Simple parsing logic
        keywords = [k.strip() for k in response.split(',')]
        self.log(f"Generated {len(keywords)} keywords for {product_name}")
        return keywords

    def analyze_ad_performance(self, ad_data: Dict[str, Any]) -> str:
        """
        Analyze ad stats (ROAS, CTR, Clicks).
        Data format: {'spend': 100, 'revenue': 500, 'clicks': 200, 'impressions': 10000}
        """
        roas = ad_data.get('revenue', 0) / ad_data.get('spend', 1) if ad_data.get('spend') else 0
        ctr = (ad_data.get('clicks', 0) / ad_data.get('impressions', 1)) * 100 if ad_data.get('impressions') else 0
        
        prompt = f"""
        Analise a performance deste anúncio na Shopee:
        - Gasto: R$ {ad_data.get('spend')}
        - Faturamento: R$ {ad_data.get('revenue')}
        - ROAS: {roas:.2f}x
        - CTR: {ctr:.2f}%
        
        Isso é bom ou ruim? O que devo fazer? Responda em 1 parágrafo tático e direto.
        """
        advice = llm_client.generate_content(prompt)
        return advice

    def run(self, *args, **kwargs):
        pass
