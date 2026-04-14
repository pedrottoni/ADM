"""
SalesService — Central service that links financial transactions to product inventory.

When a sale (INCOME transaction) is registered, this service:
1. Matches the product name to existing Products (fuzzy match)
2. Decrements Product.stock
3. Decrements InventoryItem.stock via ProductComponent multipliers
"""
from difflib import SequenceMatcher
from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select
from core.database.models import Product, InventoryItem, ProductComponent, Transaction
from core.database.engine import get_session


class SalesService:
    MATCH_THRESHOLD = 0.55  # 55% similarity minimum

    def match_product(self, product_name: str, user_id: int, session: Session) -> Optional[Product]:
        """
        Fuzzy-match a product name against all Products in the database.
        Returns the best matching Product or None.
        """
        if not product_name or not product_name.strip():
            return None
            
        products = session.exec(select(Product).where(Product.user_id == user_id)).all()
        if not products:
            return None
        
        best_match = None
        best_ratio = 0.0
        
        clean_name = product_name.strip().lower()
        
        for product in products:
            product_title = product.title.strip().lower()
            
            # Exact match first
            if clean_name == product_title:
                return product
            
            # Check if one contains the other
            if clean_name in product_title or product_title in clean_name:
                ratio = 0.85  # High score for containment
            else:
                ratio = SequenceMatcher(None, clean_name, product_title).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = product
        
        if best_ratio >= self.MATCH_THRESHOLD:
            return best_match
        
        return None

    def process_sale(
        self, 
        product: Product, 
        quantity: int, 
        session: Session
    ) -> Dict[str, Any]:
        """
        Decrements stock for a matched product and its inventory components.
        
        Returns dict with details of what was updated.
        """
        result = {
            "product_id": product.id,
            "product_title": product.title,
            "stock_before": product.stock,
            "inventory_updates": []
        }
        
        # 1. Decrement Product.stock (Shopee stock)
        product.stock = max(product.stock - quantity, 0)
        result["stock_after"] = product.stock
        session.add(product)
        
        # 2. Decrement InventoryItem.stock via ProductComponent multipliers
        components = session.exec(
            select(ProductComponent).where(ProductComponent.product_id == product.id)
        ).all()
        
        if components:
            for comp in components:
                inv_item = session.get(InventoryItem, comp.inventory_item_id)
                if inv_item:
                    units_to_deduct = quantity * comp.quantity
                    old_stock = inv_item.stock
                    inv_item.stock = max(inv_item.stock - units_to_deduct, 0)
                    session.add(inv_item)
                    result["inventory_updates"].append({
                        "item_name": inv_item.name,
                        "old_stock": old_stock,
                        "new_stock": inv_item.stock,
                        "deducted": units_to_deduct
                    })
        
        return result

    def check_duplicate(
        self, 
        date, 
        description: str, 
        amount: float, 
        user_id: int, 
        session: Session
    ) -> bool:
        """
        Check if a transaction with the same date, description, and amount already exists.
        Returns True if duplicate found.
        """
        import pandas as pd
        from datetime import datetime
        
        # Normalize date
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        existing = session.exec(
            select(Transaction).where(
                Transaction.user_id == user_id,
                Transaction.description == description,
                Transaction.amount == amount,
                Transaction.type == "INCOME"
            )
        ).all()
        
        if not existing:
            return False
        
        # Check if any existing transaction has the same date (day-level)
        for txn in existing:
            txn_date = txn.date
            if isinstance(txn_date, datetime):
                txn_date = txn_date.date()
            
            check_date = date
            if isinstance(check_date, datetime):
                check_date = check_date.date()
            elif hasattr(check_date, 'date'):
                check_date = check_date.date()
                
            if txn_date == check_date:
                return True
        
        return False

    def process_income_batch(
        self,
        sales_data: List[Dict[str, Any]],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Process a batch of sales. For each sale:
        1. Check for duplicates
        2. Match product
        3. Save transaction
        4. Update stock
        
        Returns summary with matched, unmatched, and duplicated items.
        """
        session = next(get_session())
        
        matched = []
        unmatched = []
        duplicated = []
        
        for sale in sales_data:
            description = sale.get("product", sale.get("description", "Venda"))
            amount = float(sale.get("amount", 0))
            quantity = int(sale.get("quantity", 1))
            date = sale.get("date")
            
            # 1. Check duplicates
            if self.check_duplicate(date, description, amount, user_id, session):
                duplicated.append({"description": description, "amount": amount, "date": str(date)})
                continue
            
            # 2. Match product
            product = self.match_product(description, user_id, session)
            
            # 3. Create transaction
            import pandas as pd
            txn = Transaction(
                date=pd.to_datetime(date) if date else None,
                type="INCOME",
                category="Sale",
                description=description,
                amount=amount,
                quantity=quantity,
                product_id=product.id if product else None,
                user_id=user_id
            )
            session.add(txn)
            
            # 4. Update stock if matched
            if product:
                stock_result = self.process_sale(product, quantity, session)
                matched.append({
                    "description": description,
                    "amount": amount,
                    "product_title": product.title,
                    **stock_result
                })
            else:
                unmatched.append({
                    "description": description,
                    "amount": amount,
                    "date": str(date),
                    "quantity": quantity
                })
        
        session.commit()
        
        return {
            "success": True,
            "total": len(sales_data),
            "matched": matched,
            "unmatched": unmatched,
            "duplicated": duplicated,
            "matched_count": len(matched),
            "unmatched_count": len(unmatched),
            "duplicated_count": len(duplicated)
        }
