import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'ivs.db')
    if not os.path.exists(db_path):
        print("Database not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_to_add = [
        ('province', 'VARCHAR(100)'),
        ('city', 'VARCHAR(100)'),
        ('barangay', 'VARCHAR(100)'),
        ('street', 'VARCHAR(100)'),
        ('house_number', 'VARCHAR(50)'),
        ('zipcode', 'VARCHAR(20)'),
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE address ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to address table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
