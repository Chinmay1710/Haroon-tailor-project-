import sqlite3
import os
from app.config import DATABASE_PATH

db_path = DATABASE_PATH
print("DB Path:", db_path)

def upgrade():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE shop_settings ADD COLUMN twilio_account_sid VARCHAR(255) DEFAULT ''")
    except Exception as e:
        print("twilio_account_sid:", e)
    try:
        cursor.execute("ALTER TABLE shop_settings ADD COLUMN twilio_auth_token VARCHAR(255) DEFAULT ''")
    except Exception as e:
        print("twilio_auth_token:", e)
    try:
        cursor.execute("ALTER TABLE shop_settings ADD COLUMN twilio_sender_number VARCHAR(20) DEFAULT ''")
    except Exception as e:
        print("twilio_sender_number:", e)
    
    conn.commit()
    print("Done")
    conn.close()

if __name__ == "__main__":
    upgrade()
