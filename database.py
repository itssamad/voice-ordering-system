import sqlite3

DB_NAME = "orders.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            speech_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            quantity INTEGER,
            product_type TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            phone_number TEXT PRIMARY KEY,
            quantity INTEGER,
            product_type TEXT,
            address TEXT
        )
        """)

        conn.commit()


def save_call(phone_number, speech_text):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO calls (phone_number, speech_text)
        VALUES (?, ?)
        """, (phone_number, speech_text))
        conn.commit()


def create_or_reset_session(phone_number):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO sessions (phone_number, quantity, product_type, address)
        VALUES (?, NULL, NULL, NULL)
        """, (phone_number,))
        conn.commit()


def update_session_quantity(phone_number, quantity):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE sessions
        SET quantity = ?
        WHERE phone_number = ?
        """, (quantity, phone_number))
        conn.commit()


def update_session_product(phone_number, product_type):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE sessions
        SET product_type = ?
        WHERE phone_number = ?
        """, (product_type, phone_number))
        conn.commit()


def update_session_address(phone_number, address):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE sessions
        SET address = ?
        WHERE phone_number = ?
        """, (address, phone_number))
        conn.commit()


def get_session(phone_number):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT phone_number, quantity, product_type, address
        FROM sessions
        WHERE phone_number = ?
        """, (phone_number,))
        return cursor.fetchone()


def save_order(phone_number, quantity, product_type, address):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO orders (phone_number, quantity, product_type, address)
        VALUES (?, ?, ?, ?)
        """, (phone_number, quantity, product_type, address))
        conn.commit()


def delete_session(phone_number):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM sessions
        WHERE phone_number = ?
        """, (phone_number,))
        conn.commit()