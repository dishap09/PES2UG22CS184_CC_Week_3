import os
import sqlite3
from contextlib import contextmanager
from functools import lru_cache

DB_PATH = 'products.db'

# Context manager for managing database connections
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def connect(path):
    exists = os.path.exists(path)
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        if not exists:
            create_tables(conn)


def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            cost REAL NOT NULL,
            qty INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    seed_products(conn)


def seed_products(conn):
    # Seed products (use executemany for batching)
    products = [
        ('Backpack', 'A durable and stylish backpack for daily use.', 800.0, 10),
        ('Wireless Mouse', 'A sleek and ergonomic wireless mouse with a long battery life.', 800.0, 20),
        ('Bluetooth Speaker', 'A portable Bluetooth speaker with high-quality sound and deep bass.', 3000.0, 30),
        # ... add the rest of the products here ...
        ('Portable Projector', 'A mini portable projector with HD resolution.', 15000.0, 8)
    ]
    conn.executemany('INSERT INTO products (name, description, cost, qty) VALUES (?, ?, ?, ?)', products)
    conn.commit()


# Use LRU Cache to cache frequent read operations
@lru_cache(maxsize=128)
def list_products():
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM products ORDER BY id ASC')
        products = cursor.fetchall()
        return [dict(row) for row in products]  # Convert to a list of dictionaries for easier processing


def add_product(product: dict):
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO products (name, description, cost, qty) VALUES (?, ?, ?, ?)',
            (product['name'], product['description'], product['cost'], product['qty'])
        )
        conn.commit()


def get_product(product_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_qty(product_id: int, qty: int):
    with get_db_connection() as conn:
        conn.execute('UPDATE products SET qty = ? WHERE id = ?', (qty, product_id))
        conn.commit()


def delete_product(product_id: int):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()


def update_product(product_id: int, product: dict):
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE products SET name = ?, description = ?, cost = ?, qty = ? WHERE id = ?',
            (product['name'], product['description'], product['cost'], product['qty'], product_id)
        )
        conn.commit()
