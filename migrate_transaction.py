from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE transaction ADD COLUMN address_id INT"))
        db.session.commit()
        print("Added address_id to transaction")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        
    try:
        db.session.execute(text("ALTER TABLE transaction ADD COLUMN payment_method VARCHAR(50)"))
        db.session.commit()
        print("Added payment_method to transaction")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
