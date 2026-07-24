import sqlite3

def add_columns():
    conn = sqlite3.connect('instance/ivs.db')
    cursor = conn.cursor()
    try:
        cursor.execute('ALTER TABLE asset ADD COLUMN views INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print(f"Column views exists or error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_columns()
