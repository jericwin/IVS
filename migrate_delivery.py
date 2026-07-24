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
        ('delivery_status', 'VARCHAR(50) DEFAULT "Pending"'),
        ('delivery_evidence_filename', 'VARCHAR(100)'),
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE `transaction` ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name} to transaction table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    # Update existing null delivery_status to 'Pending' just in case
    cursor.execute("UPDATE `transaction` SET delivery_status = 'Pending' WHERE delivery_status IS NULL")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
