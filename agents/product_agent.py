from agents.base_agent import BaseAgent
from core.llm_client import llm_client
import pandas as pd
from typing import Dict, List, Any
from core.database.engine import get_session, engine
from core.database.models import Product, ProductVariation, InventoryItem, ProductComponent
from sqlalchemy.orm import selectinload

from sqlmodel import select, or_, Session

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
        
        return self._parse_llm_response(response)

    def generate_mass_upload_csv(self, products_data: List[Dict[str, str]]) -> str:
        """
        Creates a CSV string compatible with general e-commerce uploads.
        Supports standard variations exported in rows.
        """
        if not products_data:
            return ""
            
        df = pd.DataFrame(products_data)
        
        # Create a DataFrame structured for Shopee Mass Upload (Simplified)
        # Create a DataFrame structured for Shopee Mass Upload (Simplified)
        df_export = pd.DataFrame(index=df.index)
        
        # Category ID usually required but we leave blank for user
        df_export['Nome do Produto'] = df['title'] if 'title' in df.columns else ''
        df_export['Descrição'] = df['description'] if 'description' in df.columns else ''
        df_export['Preço'] = df['price'] if 'price' in df.columns else 0.00
        df_export['Estoque'] = df['stock'] if 'stock' in df.columns else 100
        df_export['Peso (kg)'] = df['weight'] if 'weight' in df.columns else 0.5
        df_export['Capa (Nome Arquivo)'] = "" # Placeholder for manual image ref
        df_export['Imagem 1'] = ""
        df_export['Imagem 2'] = ""
        df_export['Imagem 3'] = ""
        df_export['Imagem 4'] = ""
        df_export['Imagem 5'] = ""
        
    def extract_product_info(self, image_bytes: bytes) -> str:
        """
        Step 1: Just extract raw info from the image.
        """
        vision_prompt = """
        Analise esta imagem de um produto/rótulo. 
        Extraia de forma organizada:
        1. NOME DO PRODUTO (e Variante, ex: Chocolate, Sabor Laranja)
        2. MARCA
        3. PESO/VOLUME (ex: 900g, 60 caps)
        4. BREVE DESCRIÇÃO TÉCNICA (Ingredientes principais ou função).
        
        Seja preciso. Se não conseguir ler, informe 'Não foi possível ler as informações'.
        """
        extracted_info = llm_client.generate_with_image(vision_prompt, image_bytes)
        return extracted_info

    def generate_from_extracted_info(self, info_text: str) -> Dict[str, Any]:
        """
        Step 2: Take (possibly edited) info and generate full listing with search.
        """
        enrich_prompt = f"""
        Com base nestas informações de um produto:
        {info_text}
        
        PESQUISE na internet os detalhes atuais, benefícios Reais e como este produto se posiciona no mercado.
        
        Depois, siga as REGRAS DE OURO e a ESTRUTURA de copy abaixo para criar o anúncio perfeito:
        
        ESTILO DE ESCRITA (SCIENTIFIC CONVERSION):
        - Objetivo: Converter vendas passando autoridade e confiança.
        - Visual: USE EMOJIS (🧠, 💪, 😴) para quebrar o texto.
        
        ESTRUTURA OBRIGATÓRIA:
        1. Intro: O que é e para que serve.
        2. Principais Benefícios (Bullets com Emojis). 
        3. Diferenciais Nutri Active: (Fatos: Validade, Nota Fiscal, Lacre).
        
        REGRAS DE OURO:
        1. Título SEO: 50-60 caracteres, Keywords no início.
        2. Compliance: NUNCA prometa cura. Use "auxilia", "suplementa".
        
        Retorne ESTRITAMENTE neste formato:
        TÍTULO: [O título aqui]
        DESCRIÇÃO: [O texto completo da descrição aqui]
        KEYWORDS: [Lista de 15 palavras-chave separadas por vírgula]
        """
        
        # Step 2: Use default provider (OpenRouter) for generation
        response = llm_client.generate_content(enrich_prompt, use_search=False)
        return self._parse_llm_response(response)

    def _parse_llm_response(self, response: str) -> Dict[str, str]:
        """Helper to parse the TÍTULO/DESCRIÇÃO/KEYWORDS format."""
        import re
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
        
        if not match_title and not match_desc:
             lines = response.split('\n')
             if len(lines) > 0: title = lines[0]
             if len(lines) > 1: description = "\n".join(lines[1:])
                
        return {"title": title, "description": description, "keywords": keywords}

    def save_product(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Saves a product to the database."""
        try:
            with Session(engine) as session:
                new_product = Product(
                    title=data.get('title', 'Sem Título'),
                    description=data.get('description', ''),
                    keywords=data.get('keywords', ''),
                    price=data.get('price', 0.0),
                    supplier_price=data.get('supplier_price', 0.0),
                    stock=data.get('stock', 0),
                    initial_stock=data.get('initial_stock', 100),
                    sku=data.get('sku'),
                    shopee_id=data.get('shopee_id'),
                    category=data.get('category'),
                    user_id=user_id
                )
                session.add(new_product)
                session.commit()
                session.refresh(new_product)
                return {"success": True, "product_id": new_product.id}

        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_all_products(self, user_id: int) -> List[Product]:
        """Retrieves all products for a user."""
        with Session(engine) as session:
            statement = select(Product).options(selectinload(Product.components)).where(Product.user_id == user_id)
            return session.exec(statement).all()


    def update_product(self, product_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing product."""
        try:
            with Session(engine) as session:
                product = session.get(Product, product_id)
                if not product:
                    return {"success": False, "message": "Produto não encontrado"}
                
                for key, value in updates.items():
                    if hasattr(product, key):
                        setattr(product, key, value)
                
                session.add(product)
                session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Deletes a product."""
        try:
            with Session(engine) as session:
                product = session.get(Product, product_id)
                if product:
                    session.delete(product)
                    session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # --- VARIATION SPECIFIC CRUD --- #
    def get_product_variations(self, product_id: int) -> List[ProductVariation]:
        """Retrieves all variations for a product."""
        with Session(engine) as session:
            statement = select(ProductVariation).where(ProductVariation.product_id == product_id)
            return session.exec(statement).all()


    def save_variation(self, data: Dict[str, Any], product_id: int) -> Dict[str, Any]:
        """Saves a variation to the database."""
        try:
            with Session(engine) as session:
                new_var = ProductVariation(
                    name=data.get('name', 'Nova Variação'),
                    price=data.get('price', 0.0),
                    supplier_price=data.get('supplier_price', 0.0),
                    stock=data.get('stock', 0),
                    sku=data.get('sku'),
                    shopee_id=data.get('shopee_id'),
                    product_id=product_id
                )
                session.add(new_var)
                session.commit()
                session.refresh(new_var)
                return {"success": True, "variation_id": new_var.id}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_variation(self, variation_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing variation."""
        try:
            with Session(engine) as session:
                var = session.get(ProductVariation, variation_id)
                if not var:
                    return {"success": False, "message": "Variação não encontrada"}
                
                for key, value in updates.items():
                    if hasattr(var, key):
                        setattr(var, key, value)
                
                session.add(var)
                session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_variation(self, variation_id: int) -> Dict[str, Any]:
        """Deletes a variation."""
        try:
            with Session(engine) as session:
                var = session.get(ProductVariation, variation_id)
                if var:
                    session.delete(var)
                    session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def process_csv_import(self, file, user_id: int) -> Dict[str, Any]:
        """Imports products from a Shopee-like CSV."""
        try:
            df = pd.read_csv(file)
            
            # Flexible mapping for Shopee columns
            mapping = {
                'Nome do Produto': 'title',
                'Descrição': 'description',
                'Preço': 'price',
                'Estoque': 'stock',
                'Código SKU': 'sku',
                'Category ID': 'category'
            }
            
            imported_count = 0
            session = next(get_session())
            
            for _, row in df.iterrows():
                product_data = {}
                for shopee_col, model_attr in mapping.items():
                    if shopee_col in df.columns:
                        val = row[shopee_col]
                        # Type conversion
                        if model_attr == 'price': val = float(str(val).replace('R$', '').replace(',', '.').strip() or 0)
                        elif model_attr == 'stock': val = int(val or 0)
                        product_data[model_attr] = val
                
                if 'title' in product_data:
                    new_prod = Product(**product_data, user_id=user_id)
                    session.add(new_prod)
                    imported_count += 1
            
            session.commit()
            return {"success": True, "count": imported_count}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_all_inventory_items(self, user_id: int) -> List[InventoryItem]:
        """Retrieves all physical inventory items for a user."""
        with Session(engine) as session:
            statement = select(InventoryItem).where(InventoryItem.user_id == user_id)
            return session.exec(statement).all()


    def update_inventory_item(self, item_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a physical inventory item."""
        try:
            with Session(engine) as session:
                item = session.get(InventoryItem, item_id)
                if not item:
                    return {"success": False, "message": "Item não encontrado"}
                
                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                
                session.add(item)
                session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_product_components(self, product_id: int) -> List[ProductComponent]:
        """Retrieves all components (physical items) linked to a virtual product."""
        with Session(engine) as session:
            statement = select(ProductComponent).where(ProductComponent.product_id == product_id)
            return session.exec(statement).all()


    def add_product_component(self, product_id: int, inventory_item_id: int, quantity: int) -> Dict[str, Any]:
        """Links an inventory item to a product with a specific quantity."""
        try:
            with Session(engine) as session:
                new_comp = ProductComponent(
                    product_id=product_id,
                    inventory_item_id=inventory_item_id,
                    quantity=quantity
                )
                session.add(new_comp)
                session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_product_component(self, component_id: int) -> Dict[str, Any]:
        """Removes a link between an inventory item and a product."""
        try:
            with Session(engine) as session:
                comp = session.get(ProductComponent, component_id)
                if comp:
                    session.delete(comp)
                    session.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_low_stock_items(self, user_id: int) -> List[InventoryItem]:
        """Returns inventory items where stock <= min_stock."""
        with Session(engine) as session:
            statement = select(InventoryItem).where(
                InventoryItem.user_id == user_id,
                InventoryItem.stock <= InventoryItem.min_stock
            )
            return session.exec(statement).all()


    def generate_image_prompt(self, title: str, description: str) -> str:
        """Generates 3 image prompts for Midjourney/DALL-E."""
        prompt = f"""
        Você é um Diretor de Arte Especialista em Fotografia de Produto para E-commerce.
        Crie 3 variações de prompts para gerar imagens realistas do seguinte produto:
        Título: {title}
        Descrição: {description}
        
        DIRETRIZES:
        - Estilo: Fotografia comercial, ultra-detalhada, iluminação de estúdio (softbox).
        - Cores: Paleta limpa, tons que remetam a saúde e bem-estar.
        - Fundo: Minimalista, fundo infinito ou ambiente de casa premium.
        
        FORMATO DE RESPOSTA:
        VARIAÇÃO 1 (Estúdio): [Prompt em inglês]
        VARIAÇÃO 2 (Lifestyle/Contexto): [Prompt em inglês]
        VARIAÇÃO 3 (Foco em Detalhe): [Prompt em inglês]
        """
        response = llm_client.generate_content(prompt)
        return response

    def run(self, *args, **kwargs):
        """
        Placeholder execution method.
        """
        pass
