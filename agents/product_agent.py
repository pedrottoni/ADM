from agents.base_agent import BaseAgent
from core.llm_client import llm_client
import pandas as pd
from typing import Dict, List

class ProductAgent(BaseAgent):
    def __init__(self):
        super().__init__("Product Factory")

    def generate_listing(self, product_name: str, key_benefits: str, ingredients: str) -> Dict[str, str]:
        """
        Generates a Title, Description and Keywords optimized for Shopee 2025 & Nutri Active.
        """
        prompt = f"""
        Você é um Redator Especialista em Suplementos (Alta Conversão + Rigor Técnico).
        Crie um kit de cadastro para o produto: '{product_name}' da marca 'Nutri Active'.
        
        Dados:
        - Ingredientes: {ingredients}
        - Foco/Benefícios: {key_benefits}
        
        ESTILO DE ESCRITA (SCIENTIFIC CONVERSION):
        - Objetivo: Converter vendas passando autoridade e confiança.
        - Visual: USE EMOJIS (🧠, 💪, 😴) para quebrar o texto.
        - Títulos dos Tópicos: Use termos TÉCNICOS e CLAROS. (Ex: "🧠 Função Cognitiva e Foco" / "💪 Recuperação Muscular"). Nada de "Mente Afiada" ou termos infantis.
        - Texto dos Tópicos: Explique o benefício de forma persuasiva.
        
        ESTRUTURA OBRIGATÓRIA:
        1. Intro: O que é e para que serve (Direto).
        2. Principais Benefícios (Bullets com Emojis + Título Técnico). 
        3. Diferenciais Nutri Active: (Fatos: Validade, Nota Fiscal, Lacre).
        
        ❌ PROIBIDO (O "ANTI-FLUFF"):
        - Frases vazias: "Você merece", "O melhor da região", "Premium", "Produto de valor", "Sinergia perfeita", "Incrível".
        - NÃO use adjetivos vazios. Se o produto é bom, diga O QUE ele tem (Ex: "Matéria-prima importada").
        
        REGRAS DE OURO:
        1. Título SEO: 50-60 caracteres, Keywords no início.
        2. Compliance: NUNCA prometa cura. Use "auxilia", "suplementa".
        
        Retorne ESTRITAMENTE neste formato:
        TÍTULO: [O título aqui]
        DESCRIÇÃO: [O texto completo da descrição aqui]
        KEYWORDS: [Lista de 15 palavras-chave separadas por vírgula]
        """
        
        response = llm_client.generate_content(prompt)
        
        import re
        
        # Robust Regex Parsing
        # Pattern looks for TÍTULO:, DESCRIÇÃO:, KEYWORDS: (case insensitive) followed by content until the next tag or end of string
        patterns = {
            'title': r'(?:TÍTULO|TITULO):\s*(.*?)(?=(?:DESCRIÇÃO|DESCRICAO|KEYWORDS|KEY WORDS)|$)',
            'description': r'(?:DESCRIÇÃO|DESCRICAO):\s*(.*?)(?=(?:TÍTULO|TITULO|KEYWORDS|KEY WORDS)|$)',
            'keywords': r'(?:KEYWORDS|KEY WORDS|PALAVRAS-CHAVE):\s*(.*?)(?=(?:TÍTULO|TITULO|DESCRIÇÃO|DESCRICAO)|$)'
        }
        
        title = "Título não detectado"
        description = response
        keywords = ""
        
        flags = re.IGNORECASE | re.DOTALL
        
        match_title = re.search(patterns['title'], response, flags)
        if match_title: title = match_title.group(1).strip()
        
        match_desc = re.search(patterns['description'], response, flags)
        if match_desc: description = match_desc.group(1).strip()
        
        match_keys = re.search(patterns['keywords'], response, flags)
        if match_keys: keywords = match_keys.group(1).strip()
        
        # Fallback if regex fails completely (e.g. model output plain text)
        if not match_title and not match_desc:
             lines = response.split('\n')
             if len(lines) > 0: title = lines[0]
             if len(lines) > 1: description = "\n".join(lines[1:])
                
        return {"title": title, "description": description, "keywords": keywords}

    def generate_mass_upload_csv(self, products_data: List[Dict[str, str]]) -> str:
        """
        Creates a CSV string compatible with general e-commerce uploads.
        """
        if not products_data:
            return ""
            
        df = pd.DataFrame(products_data)
        
        # Create a DataFrame structured for Shopee Mass Upload (Simplified)
        df_export = pd.DataFrame()
        
        # Category ID usually required but we leave blank for user
        df_export['Nome do Produto'] = df.get('title', '')
        df_export['Descrição'] = df.get('description', '')
        df_export['Preço'] = df.get('price', 0.00)
        df_export['Estoque'] = df.get('stock', 100)
        df_export['Peso (kg)'] = df.get('weight', 0.5)
        df_export['Capa (Nome Arquivo)'] = "" # Placeholder for manual image ref
        df_export['Imagem 1'] = ""
        df_export['Imagem 2'] = ""
        df_export['Imagem 3'] = ""
        df_export['Imagem 4'] = ""
        df_export['Imagem 5'] = ""
        
    def run(self, *args, **kwargs):
        """
        Placeholder execution method.
        In the future, this could automate the full flow of generating products + CSV.
        """
        pass
