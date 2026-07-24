import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ivs.db')
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create asset_variation table
    try:
        cursor.execute("""
        CREATE TABLE asset_variation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            image_filename VARCHAR(100) NOT NULL,
            FOREIGN KEY(asset_id) REFERENCES asset(id)
        )
        """)
        print("Created asset_variation table.")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print("Table asset_variation already exists.")
        else:
            print(f"Error creating asset_variation table: {e}")

    # Add variation_name to transaction table
    try:
        cursor.execute("ALTER TABLE `transaction` ADD COLUMN variation_name VARCHAR(100)")
        print("Added column variation_name to transaction table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column variation_name already exists.")
        else:
            print(f"Error adding variation_name: {e}")

    # For existing assets, create a default variation
    cursor.execute("SELECT id, name, image_filename FROM asset")
    assets = cursor.fetchall()
    
    for asset_id, name, image_filename in assets:
        # Check if it already has a variation
        cursor.execute("SELECT COUNT(*) FROM asset_variation WHERE asset_id = ?", (asset_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO asset_variation (asset_id, name, image_filename) VALUES (?, ?, ?)",
                           (asset_id, "Default", image_filename))
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
