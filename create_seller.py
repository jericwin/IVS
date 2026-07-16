from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if seller exists
    seller = User.query.filter_by(email='seller@ivs.com').first()
    if not seller:
        new_seller = User(
            first_name='Admin',
            last_name='Seller',
            email='seller@ivs.com',
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
            role='seller'
        )
        db.session.add(new_seller)
        db.session.commit()
        print("Seller account created successfully!")
    else:
        print("Seller account already exists!")
