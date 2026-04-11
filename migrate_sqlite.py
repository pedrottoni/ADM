import sqlite3

def migrate():
    db_path = r"c:\Proiectum\Loja\ADM\database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    queries = [
        "ALTER TABLE product ADD COLUMN initial_stock INTEGER DEFAULT 100"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
            print(f"Sucesso: {q}")
        except sqlite3.OperationalError as e:
            print(f"Erro ao executar '{q}' (provavelmente a coluna já existe): {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
