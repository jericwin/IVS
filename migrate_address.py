from app import app, db
from models import User, Address

with app.app_context():
    # Create new tables (like address)
    db.create_all()
    print("Created tables.")

    # Migrate data
    users = User.query.all()
    for u in users:
        if u.address and u.phone:
            # Check if address already exists for this user
            existing = Address.query.filter_by(user_id=u.id).first()
            if not existing:
                addr = Address(
                    user_id=u.id,
                    recipient_name=f"{u.first_name} {u.last_name}",
                    phone=u.phone,
                    street_address=u.address,
                    is_default=True
                )
                db.session.add(addr)
    
    db.session.commit()
    print("Migrated existing user addresses to Address table.")
