import sqlite3

def migrate():
    print("Migrating database to add WebMCP support...")
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    try:
        # Add has_webmcp column to bridges
        try:
            cursor.execute("ALTER TABLE bridges ADD COLUMN has_webmcp BOOLEAN DEFAULT 0")
            print("Added has_webmcp column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("has_webmcp column already exists.")
            else:
                print(f"Error adding has_webmcp: {e}")

        # Add webmcp_tool_count column to bridges
        try:
            cursor.execute("ALTER TABLE bridges ADD COLUMN webmcp_tool_count INTEGER DEFAULT 0")
            print("Added webmcp_tool_count column.")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print("webmcp_tool_count column already exists.")
            else:
                print(f"Error adding webmcp_tool_count: {e}")

        # Create webmcp_tools table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webmcp_tools (
                    id TEXT PRIMARY KEY,
                    bridge_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    tool_type TEXT NOT NULL,
                    description TEXT,
                    parameters_schema JSON,
                    is_available BOOLEAN DEFAULT 1,
                    last_verified_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(bridge_id) REFERENCES bridges(id) ON DELETE CASCADE
                )
            """)
            print("Created webmcp_tools table.")
        except sqlite3.OperationalError as e:
            print(f"Error creating webmcp_tools table: {e}")
            
        conn.commit()
        print("Migration complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
