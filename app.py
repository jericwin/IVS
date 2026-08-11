import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from models import db, User
from routes import oauth
from routes.auth import auth_bp
from routes.main import main_bp
from routes.buyer import buyer_bp
from routes.seller import seller_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ivs-super-secret-key-123')

# Security: Enforce secure session cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Security: Enable CSRF Protection
csrf = CSRFProtect(app)

# Security: Enable HTTP Security Headers via Talisman
# We use content_security_policy=False temporarily to avoid breaking inline scripts/styles until fully configured.
Talisman(app, content_security_policy=False, force_https=False) 

# OAuth Setup
oauth.init_app(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'placeholder_client_id'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'placeholder_client_secret'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

# Database Setup
database_url = os.environ.get("DATABASE_URL", "sqlite:///ivs.db")

# Neon DBs add query parameters like ?sslmode=require that pg8000 does not support
if "?" in database_url:
    database_url = database_url.split("?")[0]

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Auto-create all tables and seed default accounts on startup
with app.app_context():
    db.create_all()
    
    from werkzeug.security import generate_password_hash
    def seed_user(first, last, email, password, role, employer_id=None):
        if not User.query.filter_by(email=email).first():
            u = User(
                first_name=first, last_name=last, email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
                role=role, employer_id=employer_id
            )
            db.session.add(u)
            db.session.commit()

    seed_user('Admin', 'Seller',  'seller@ivs.com',           'seller123',  'seller')
    seed_user('Jeric', 'Punay',   'punay.jeric@gmail.com',    'jeric123',   'seller')
    seed_user('Jasmine', 'Araza', 'jasmine.araza@gmail.com',  'jasmine123', 'buyer')
    seed_user('Urahara', 'Kisuke','uarhara.kisuke@gmail.com', 'kisuke123',  'buyer')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(seller_bp)

@app.context_processor
def inject_global_counts():
    from flask_login import current_user
    counts = {'pending_orders_count': 0, 'cart_item_count': 0}
    if current_user.is_authenticated:
        if current_user.role in ['seller', 'employee']:
            from models import Transaction, Asset
            pending_count = Transaction.query.join(Asset).filter(
                Asset.seller_id == current_user.store_owner_id,
                (Transaction.delivery_status == None) | (Transaction.delivery_status == 'Pending')
            ).count()
            counts['pending_orders_count'] = pending_count
        elif current_user.role == 'buyer':
            from models import CartItem
            counts['cart_item_count'] = CartItem.query.filter_by(buyer_id=current_user.id).count()
    return counts

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
