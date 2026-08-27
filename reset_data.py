import os
from app.config import DATABASE_PATH

print(f"Checking database at: {DATABASE_PATH}")
if os.path.exists(DATABASE_PATH):
    os.remove(DATABASE_PATH)
    print("✅ All data has been CLEARED!")
    print("If you run the app now, it will start completely empty.")
else:
    print("Database already empty or not found.")
