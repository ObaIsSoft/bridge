
import sqlite3
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def migrate():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # 1. Add Column
    print("Adding slug column...")
    try:
        cursor.execute("ALTER TABLE bridges ADD COLUMN slug VARCHAR(255)")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("Column already exists. Skipping.")
        else:
            print(f"Note: {e}")

    # 2. Backfill Slugs
    print("Backfilling slugs...")
    cursor.execute("SELECT id, name FROM bridges WHERE slug IS NULL")
    bridges = cursor.fetchall()
    
    for bridge_id, name in bridges:
        if not name:
            slug = f"bridge-{bridge_id[:8]}"
        else:
            slug = slugify(name)
        
        # Check uniqueness handling (simple append for now)
        base_slug = slug
        count = 1
        while True:
            cursor.execute("SELECT 1 FROM bridges WHERE slug = ? AND id != ?", (slug, bridge_id))
            if cursor.fetchone():
                slug = f"{base_slug}-{count}"
                count += 1
            else:
                break
        
        print(f"Updating {bridge_id} ({name}) -> {slug}")
        cursor.execute("UPDATE bridges SET slug = ? WHERE id = ?", (slug, bridge_id))

    # 3. Create Index
    print("Creating unique index...")
    try:
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_bridges_slug ON bridges(slug)")
    except Exception as e:
        print(f"Index creation note: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
