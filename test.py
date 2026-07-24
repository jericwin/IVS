import app
from models import db, User
from flask_login import login_user
for u in app.app.app_context().push() or User.query.all():
    print(f'User {u.email} ({u.role}):')
    with app.app.test_client() as c:
        with c.session_transaction() as sess:
            sess['_user_id'] = str(u.id)
            sess['_fresh'] = True
        for route in ['/buyer/dashboard', '/seller/dashboard', '/seller/analytics', '/profile']:
            resp = c.get(route)
            print(f'  {route}: {resp.status_code}')
