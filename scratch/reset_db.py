from sqlmodel import Session, select
from core.database.engine import engine
from core.database.models import Transaction, InventoryItem, Product

def reset_data():
    with Session(engine) as session:
        # 1. Delete all income transactions (sales)
        statement = select(Transaction).where(Transaction.type == "INCOME")
        results = session.exec(statement).all()
        for txn in results:
            session.delete(txn)
        print(f"DONE: {len(results)} sales transactions deleted.")
        
        # 2. Reset Physical Inventory
        inv_items = session.exec(select(InventoryItem)).all()
        for item in inv_items:
            item.stock = 600
            item.initial_stock = 600
            session.add(item)
        print(f"DONE: {len(inv_items)} inventory items reset to 600 stock.")
        
        # 3. Reset Virtual Products (Shopee Stock)
        products = session.exec(select(Product)).all()
        for p in products:
            multiplier = 1
            if p.components:
                multiplier = sum(comp.quantity for comp in p.components)
            
            p.stock = 600 // multiplier if multiplier > 0 else 600
            p.initial_stock = 600 // multiplier if multiplier > 0 else 600
            session.add(p)
        print(f"DONE: {len(products)} virtual products stock recalculated.")
        
        session.commit()

if __name__ == "__main__":
    reset_data()
