from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR(20)"))
        db.session.commit()
        print("Added phone column")
    except Exception as e:
        print(f"Error adding phone: {e}")
        db.session.rollback()
        
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN address TEXT"))
        db.session.commit()
        print("Added address column")
    except Exception as e:
        print(f"Error adding address: {e}")
        db.session.rollback()

print("Migration complete.")
