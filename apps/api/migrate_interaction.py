
import sqlite3

def migrate():
    print("Migrating database to add Interaction columns...")
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Add auth_config column
        try:
            cursor.execute("ALTER TABLE bridges ADD COLUMN auth_config JSON")
            print("Added auth_config column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("auth_config column already exists.")
            else:
                print(f"Error adding auth_config: {e}")

        # Add interaction_script column
        try:
            cursor.execute("ALTER TABLE bridges ADD COLUMN interaction_script JSON")
            print("Added interaction_script column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("interaction_script column already exists.")
            else:
                print(f"Error adding interaction_script: {e}")
                
        conn.commit()
        print("Migration complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
