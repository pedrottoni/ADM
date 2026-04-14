import re
import sqlite3
from sqlmodel import Session, select, create_engine, SQLModel
from core.database.models import Product, InventoryItem, ProductComponent

def migrate_to_bundles():
    db_path = r"sqlite:///c:\Proiectum\Loja\ADM\database.db"
    engine = create_engine(db_path)
    
    # 1. Criar novas tabelas via SQLModel
    print("Criando tabelas...")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Verificar se já existem itens de inventário para não duplicar se rodar duas vezes
        existing_inventories = session.exec(select(InventoryItem)).all()
        if existing_inventories:
            print("Inventário já migrado anteriormente.")
            return

        products = session.exec(select(Product)).all()
        inventory_map = {} # base_name -> InventoryItem
        
        # 2. Iterar sobre todos anúncios e deduzir os itens do armazém
        for p in products:
            multiplier = 1
            match = re.search(r'- (\d+)x$', p.title.strip())
            base_name = p.title.strip()
            
            if match:
                multiplier = int(match.group(1))
                base_name = re.sub(r' - \d+x$', '', p.title.strip()).strip()
            
            # Se a master item for this base product doesn't exist, create it
            if base_name not in inventory_map:
                inv_item = InventoryItem(
                    name=base_name,
                    supplier_price=p.supplier_price,
                    stock=p.stock,
                    initial_stock=p.initial_stock,
                    user_id=p.user_id
                )
                session.add(inv_item)
                inventory_map[base_name] = inv_item
        
        # Flush to get IDs for inventory items
        session.commit()
        
        # 3. Vincular Anúncios ao Inventário via Component (Multiplicadores)
        print("Mapeando componentes e multiplicadores...")
        for p in products:
            multiplier = 1
            match = re.search(r'- (\d+)x$', p.title.strip())
            base_name = p.title.strip()
            
            if match:
                multiplier = int(match.group(1))
                base_name = re.sub(r' - \d+x$', '', p.title.strip()).strip()
                
            inv_item = inventory_map[base_name]
            
            component = ProductComponent(
                quantity=multiplier,
                product_id=p.id,
                inventory_item_id=inv_item.id
            )
            session.add(component)
        
        session.commit()
    print("Migração concluída com sucesso! Os produtos de inventário foram unificados.")

if __name__ == "__main__":
    migrate_to_bundles()
