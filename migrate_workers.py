import sqlite3

def migrate_db():
    conn = sqlite3.connect('app/database/tailor_shop.db')
    cursor = conn.cursor()
    
    # Add columns to workers table if they don't exist
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN worker_type VARCHAR(20) DEFAULT 'PIECE_RATE' NOT NULL")
    except sqlite3.OperationalError:
        pass # Column might already exist
        
    try:
        cursor.execute("ALTER TABLE workers ADD COLUMN daily_rate FLOAT DEFAULT 0.0 NOT NULL")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()
    
    # Now use SQLAlchemy to create new tables
    from app.database.engine import init_db
    init_db()
    
    print("Database migration complete.")

if __name__ == "__main__":
    migrate_db()
