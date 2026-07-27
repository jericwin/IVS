from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE "transaction" ADD COLUMN buyer_hidden BOOLEAN DEFAULT 0'))
        db.session.commit()
        print("Added buyer_hidden column")
    except Exception as e:
        print(f"Error adding buyer_hidden: {e}")
        db.session.rollback()

print("Migration complete.")
