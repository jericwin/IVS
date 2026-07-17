"""
init_db.py - Run this ONCE after deploying to seed the database with initial data.
Usage: python init_db.py
"""
from app import app, db
from models import User, Asset, ActivityLog
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    print("✅ Tables created.")

    # Only seed if no users exist yet
    if User.query.count() == 0:
        users = [
            User(
                first_name='Jeric',
                last_name='Punay',
                email='punay.jeric@gmail.com',
                password_hash='pbkdf2:sha256:600000$xQgzxR5lfecsPjZR$654429fc9a766082b08f316bae1acc827d094c77c0f02f72448d8ea0a17ec00e',
                role='seller'
            ),
            User(
                first_name='Admin',
                last_name='Seller',
                email='seller@ivs.com',
                password_hash='pbkdf2:sha256:600000$zOf08c305HzA2Noc$79d6c7834b771078206c2d9f08b3a4c72e2c00abf6a9bd3ad1ac33a89998c9ea',
                role='seller'
            ),
            User(
                first_name='Urahara',
                last_name='Kisuke',
                email='uarhara.kisuke@gmail.com',
                password_hash='pbkdf2:sha256:600000$bmBfxBVfoGUx4PzB$079a6546f0c0772cfa5eb3517f92f935a834d4fb3adc639e55c03522bfa7777c',
                role='buyer'
            ),
            User(
                first_name='Jasmine',
                last_name='Araza',
                email='jasmine.araza@gmail.com',
                password_hash='pbkdf2:sha256:600000$LJD77kEbhzFb37TC$21124182c9544aa52cd86a7d51ac726db814fa6a6e1a517653a6a60e195e8e56',
                role='buyer'
            ),
        ]
        db.session.add_all(users)
        db.session.commit()
        print("✅ Seeded 4 users.")
    else:
        print("ℹ️  Users already exist, skipping seed.")

    print("🎉 Database initialization complete!")
