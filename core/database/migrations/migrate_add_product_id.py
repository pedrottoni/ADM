"""
Migration script to add product_id and quantity columns to the Transaction table.
Run this ONCE to update the existing database schema.
"""
import sqlite3

def migrate():
    db_path = r"c:\Proiectum\Loja\ADM\database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute('PRAGMA table_info("transaction")')
    columns = [col[1] for col in cursor.fetchall()]
    
    if "product_id" not in columns:
        print("Adding 'product_id' column to transaction table...")
        cursor.execute('ALTER TABLE "transaction" ADD COLUMN product_id INTEGER REFERENCES product(id)')
    else:
        print("'product_id' column already exists.")
    
    if "quantity" not in columns:
        print("Adding 'quantity' column to transaction table...")
        cursor.execute('ALTER TABLE "transaction" ADD COLUMN quantity INTEGER DEFAULT 1')
    else:
        print("'quantity' column already exists.")
    
    conn.commit()
    conn.close()
    print("✅ Migration complete!")

if __name__ == "__main__":
    migrate()
