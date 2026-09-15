import sqlite3

DB_NAME = "orders.db"


def view_calls():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calls ORDER BY created_at DESC")
        rows = cursor.fetchall()

        print("\n--- CALLS TABLE ---\n")

        if not rows:
            print("No call records found.")
        else:
            for row in rows:
                id, phone, speech, time = row
                print(f"ID: {id}")
                print(f"Phone: {phone}")
                print(f"Speech: {speech}")
                print(f"Time: {time}")
                print("-" * 40)


def view_orders():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
        rows = cursor.fetchall()

        print("\n--- ORDERS TABLE ---\n")

        if not rows:
            print("No order records found.")
        else:
            for row in rows:
                id, phone, quantity, product_type, address, time = row
                print(f"ID: {id}")
                print(f"Phone: {phone}")
                print(f"Quantity: {quantity}")
                print(f"Type: {product_type}")
                print(f"Address: {address}")
                print(f"Time: {time}")
                print("-" * 40)


if __name__ == "__main__":
    view_calls()
    view_orders()