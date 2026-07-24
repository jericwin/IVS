from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN reset_code VARCHAR(10)"))
        db.session.commit()
        print("Added reset_code column")
    except Exception as e:
        print(f"Error adding reset_code: {e}")
        db.session.rollback()
        
    try:
        db.session.execute(text("ALTER TABLE user ADD COLUMN reset_code_expiration DATETIME"))
        db.session.commit()
        print("Added reset_code_expiration column")
    except Exception as e:
        print(f"Error adding reset_code_expiration: {e}")
        db.session.rollback()

print("Migration complete.")
