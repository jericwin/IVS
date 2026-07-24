import sqlite3

def add_columns():
    conn = sqlite3.connect('instance/ivs.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE asset ADD COLUMN is_featured_collection BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError as e:
        print(f"Column is_featured_collection exists or error: {e}")
        
    try:
        cursor.execute('ALTER TABLE asset ADD COLUMN is_featured_story BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError as e:
        print(f"Column is_featured_story exists or error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_columns()
