import sqlite3
import os

db_path = os.path.join(os.environ.get('APPDATA'), 'TailorShopManager', 'data', 'tailor_shop.db')
print(f"Updating database at {db_path}")

db = sqlite3.connect(db_path)
cursor = db.cursor()
cursor.execute("UPDATE orders SET order_number = REPLACE(order_number, 'ORD-', 'Bill-') WHERE order_number LIKE 'ORD-%'")
print(f"Rows updated: {cursor.rowcount}")
db.commit()
db.close()
