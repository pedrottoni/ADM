import sqlite3


def migrate():
    db_path = r"c:\Proiectum\Loja\ADM\database.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    queries = [
        """CREATE TABLE IF NOT EXISTS competitorlisting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            marketplace VARCHAR NOT NULL,
            competitor_title VARCHAR NOT NULL,
            competitor_price FLOAT NOT NULL,
            competitor_seller VARCHAR,
            our_price_at_time FLOAT DEFAULT 0.0,
            price_before_discount FLOAT,
            shipping_cost FLOAT,
            product_url VARCHAR NOT NULL,
            marketplace_id VARCHAR,
            rating FLOAT,
            sold_count INTEGER,
            seller_location VARCHAR,
            is_confirmed_match BOOLEAN DEFAULT 0,
            confidence_score VARCHAR,
            last_checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES product(id)
        )""",
        "CREATE INDEX IF NOT EXISTS ix_competitorlisting_product_id ON competitorlisting(product_id)",
        "CREATE INDEX IF NOT EXISTS ix_competitorlisting_marketplace ON competitorlisting(marketplace)",
    ]

    for q in queries:
        try:
            cursor.execute(q)
            print(f"Sucesso: {q[:60]}...")
        except sqlite3.OperationalError as e:
            print(f"Erro (provavelmente já existe): {e}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
