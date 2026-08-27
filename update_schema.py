import sqlite3
import os
import sys

# Ensure the app module can be found
sys.path.insert(0, os.path.dirname(__file__))

from app.config import DATABASE_PATH

def update_schema():
    if not os.path.exists(DATABASE_PATH):
        print(f"DB not found at {DATABASE_PATH}, skipping update.")
        return
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if photo_path exists in customers
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    if "photo_path" not in columns:
        print("Adding photo_path to customers table...")
        cursor.execute("ALTER TABLE customers ADD COLUMN photo_path VARCHAR(255)")
        
    # Check if image_paths exists in order_items
    cursor.execute("PRAGMA table_info(order_items)")
    columns = [col[1] for col in cursor.fetchall()]
    if "image_paths" not in columns:
        print("Adding image_paths to order_items table...")
        cursor.execute("ALTER TABLE order_items ADD COLUMN image_paths TEXT")
        
    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
