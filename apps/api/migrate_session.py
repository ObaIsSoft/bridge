
import sqlite3
import os

DB_PATH = "test.db"

def migrate_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Adding 'session_data' column to 'bridges' table...")
        cursor.execute("ALTER TABLE bridges ADD COLUMN session_data JSON")
        conn.commit()
        print("Migration successful: Added 'session_data' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column 'session_data' already exists. Skipping.")
        else:
            print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
