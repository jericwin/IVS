from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, Asset, Transaction, Address, ActivityLog

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ivs-super-secret-key-123')

# Use DATABASE_URL env var if set (for cloud MySQL/Postgres),
# otherwise fall back to a local SQLite database
database_url = os.environ.get("DATABASE_URL", "sqlite:///ivs.db")
# Render/Heroku sometimes gives postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Auto-create all tables on startup (needed for SQLite on Render)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'seller')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            if user.role in ['seller', 'employee']:
                log = ActivityLog(user_id=user.id, store_owner_id=user.store_owner_id, action='login', details=f"Logged in via IP {request.remote_addr}")
                db.session.add(log)
                db.session.commit()
                
            if user.role == 'buyer':
                return redirect(url_for('buyer_dashboard'))
            else:
                return redirect(url_for('seller_dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = 'buyer'  # Force all signups to be buyers
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('signup'))
            
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256'),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    if current_user.role in ['seller', 'employee']:
        log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.store_owner_id, action='logout', details="Logged out")
        db.session.add(log)
        db.session.commit()
    logout_user()
    return redirect(url_for('index'))

# --- Shared Routes ---

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/profile/addresses', methods=['GET', 'POST'])
@login_required
def profile_addresses():
    if request.method == 'POST':
        recipient_name = request.form.get('recipient_name')
        phone = request.form.get('phone')
        street_address = request.form.get('street_address')
        
        # If it's their first address, make it default
        existing = Address.query.filter_by(user_id=current_user.id).count()
        is_default = (existing == 0)

        addr = Address(
            user_id=current_user.id,
            recipient_name=recipient_name,
            phone=phone,
            street_address=street_address,
            is_default=is_default
        )
        db.session.add(addr)
        db.session.commit()
        flash('Address added successfully!')
        return redirect(url_for('profile_addresses'))
        
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('addresses.html', addresses=addresses)

@app.route('/profile/addresses/set_default/<int:address_id>')
@login_required
def set_default_address(address_id):
    # Reset all defaults
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    for addr in addresses:
        addr.is_default = False
    
    # Set the new default
    target = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if target:
        target.is_default = True
        db.session.commit()
        flash('Default address updated.')
    
    return redirect(url_for('profile_addresses'))

# --- Buyer Routes ---

@app.route('/buyer/dashboard')
@login_required
def buyer_dashboard():
    if current_user.role != 'buyer':
        return redirect(url_for('seller_dashboard'))
    recent_assets = Asset.query.filter_by(status='Active').order_by(Asset.created_at.desc()).limit(3).all()
    return render_template('buyer/dashboard.html', assets=recent_assets)

@app.route('/buyer/marketplace')
@login_required
def buyer_marketplace():
    assets = Asset.query.filter_by(status='Active').all()
    return render_template('buyer/marketplace.html', assets=assets)

@app.route('/buyer/purchases')
@login_required
def buyer_purchases():
    if current_user.role != 'buyer':
        return redirect(url_for('seller_dashboard'))
    transactions = Transaction.query.filter_by(buyer_id=current_user.id).order_by(Transaction.date_purchased.desc()).all()
    return render_template('buyer/purchases.html', transactions=transactions)

@app.route('/buyer/asset/<int:asset_id>')
@login_required
def buyer_asset_detail(asset_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    return render_template('buyer/asset-detail.html', asset=asset)

@app.route('/buyer/checkout/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def buyer_checkout(asset_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller_dashboard'))
    
    asset = Asset.query.get_or_404(asset_id)
    if asset.status != 'Active':
        flash('This item is no longer available.')
        return redirect(url_for('buyer_dashboard'))
        
    if request.method == 'POST':
        selected_address_id = request.form.get('address_id')
        if not selected_address_id:
            flash('Please select a delivery address.')
            return redirect(url_for('buyer_checkout', asset_id=asset_id))
            
        # Process the purchase
        payment_method = request.form.get('payment_method')
        asset.status = 'Sold'
        transaction = Transaction(
            asset_id=asset.id, 
            buyer_id=current_user.id,
            address_id=selected_address_id,
            payment_method=payment_method
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash('Purchase successful! The asset is now in your collection.')
        return redirect(url_for('buyer_dashboard'))
        
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    default_address = next((a for a in addresses if a.is_default), addresses[0] if addresses else None)
    
    return render_template('buyer/checkout.html', asset=asset, addresses=addresses, default_address=default_address)

@app.route('/buyer/settings')
@login_required
def buyer_settings():
    return render_template('buyer/settings.html')

# --- Seller Routes ---

@app.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    recent_assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).order_by(Asset.created_at.desc()).limit(3).all()
    return render_template('seller/dashboard.html', assets=recent_assets)

@app.route('/seller/asset/<int:asset_id>')
@login_required
def seller_asset_detail(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("You don't have permission to view this asset.")
        return redirect(url_for('seller_listings'))
        
    import random
    mock_views = random.randint(15, 300) # Mock views
        
    return render_template('seller/asset-detail.html', asset=asset, views=mock_views)

@app.route('/seller/listings')
@login_required
def seller_listings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).all()
    return render_template('seller/listings.html', assets=assets)

@app.route('/seller/sales')
@login_required
def seller_sales():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    
    # Get all transactions where the asset belongs to this seller
    transactions = Transaction.query.join(Asset).filter(Asset.seller_id == current_user.store_owner_id).order_by(Transaction.date_purchased.desc()).all()
    
    return render_template('seller/sales.html', transactions=transactions)

@app.route('/seller/add-asset', methods=['GET', 'POST'])
@login_required
def seller_add_asset():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category = request.form.get('category')
        description = request.form.get('description')
        
        image = request.files.get('image')
        filename = 'product-1.png'
        if image and image.filename:
            filename = image.filename
            upload_dir = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            image.save(os.path.join(upload_dir, filename))
            
        document = request.files.get('document')
        if document and document.filename:
            upload_dir = os.path.join(app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            document.save(os.path.join(upload_dir, document.filename))
        
        try:
            parsed_price = float(price) if price else 0.0
        except ValueError:
            parsed_price = 0.0
            
        try:
            parsed_stock = int(stock) if stock else 1
        except ValueError:
            parsed_stock = 1
        
        new_asset = Asset(
            name=name,
            price=parsed_price,
            stock=parsed_stock,
            category=category,
            description=description,
            seller_id=current_user.store_owner_id,
            image_filename=filename
        )
        db.session.add(new_asset)
        db.session.commit()
        
        flash('Asset posted successfully!')
        return redirect(url_for('seller_listings'))
        
    return render_template('seller/add-asset.html')

@app.route('/seller/add-employee', methods=['GET', 'POST'])
@login_required
def seller_add_employee():
    if current_user.role != 'seller':
        flash('Only store owners can add employees.')
        return redirect(url_for('seller_dashboard'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('seller_add_employee'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_employee = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hashed_password,
            role='employee',
            employer_id=current_user.id
        )
        db.session.add(new_employee)
        db.session.commit()
        
        log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.store_owner_id, action='create_employee', details=f"Created employee account for {first_name} {last_name} ({email})")
        db.session.add(log)
        db.session.commit()
        
        flash('Employee account created successfully!')
        return redirect(url_for('seller_add_employee'))
        
    employees = User.query.filter_by(role='employee', employer_id=current_user.id).all()
    return render_template('seller/add-employee.html', employees=employees)

@app.route('/seller/edit-employee/<int:id>', methods=['GET', 'POST'])
@login_required
def seller_edit_employee(id):
    if current_user.role != 'seller':
        flash('Only store owners can edit employees.')
        return redirect(url_for('seller_dashboard'))
        
    employee = User.query.get_or_404(id)
    if employee.employer_id != current_user.id:
        flash("You can only edit your own employees.")
        return redirect(url_for('seller_dashboard'))
        
    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        
        # Check email if changed
        new_email = request.form.get('email')
        if new_email != employee.email and User.query.filter_by(email=new_email).first():
            flash('Email already registered.')
            return redirect(url_for('seller_edit_employee', id=id))
        employee.email = new_email
            
        password = request.form.get('password')
        if password:  # update password only if provided
            employee.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
        log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.id, action='edit_employee', details=f"Edited employee {employee.first_name} {employee.last_name}")
        db.session.add(log)
        db.session.commit()
        
        flash('Employee updated successfully!')
        return redirect(url_for('seller_add_employee'))
        
    return render_template('seller/edit-employee.html', employee=employee)

@app.route('/seller/delete-employee/<int:id>', methods=['POST'])
@login_required
def seller_delete_employee(id):
    if current_user.role != 'seller':
        flash('Only store owners can delete employees.')
        return redirect(url_for('seller_dashboard'))
        
    employee = User.query.get_or_404(id)
    if employee.employer_id != current_user.id:
        flash("You can only delete your own employees.")
        return redirect(url_for('seller_dashboard'))
        
    employee_name = f"{employee.first_name} {employee.last_name}"
    
    db.session.delete(employee)
    
    log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.id, action='delete_employee', details=f"Deleted employee {employee_name}")
    db.session.add(log)
    db.session.commit()
    
    flash('Employee account deleted successfully.')
    return redirect(url_for('seller_add_employee'))

@app.route('/seller/logs')
@login_required
def seller_logs():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    logs = ActivityLog.query.filter_by(store_owner_id=current_user.store_owner_id).order_by(ActivityLog.timestamp.desc()).all()
    return render_template('seller/logs.html', logs=logs)

@app.route('/seller/analytics')
@login_required
def seller_analytics():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    return render_template('seller/analytics.html')

@app.route('/seller/settings')
@login_required
def seller_settings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer_dashboard'))
    return render_template('seller/settings.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
    # Simple rule-based chatbot logic
    if 'order' in message or 'purchase' in message:
        reply = "You can view your orders and their delivery status in the 'My Purchases' tab of your buyer dashboard."
    elif 'delivery' in message or 'shipping' in message or 'address' in message:
        reply = "You can manage your delivery addresses in 'My Profile'. When checking out, you'll be able to select which address to use."
    elif 'payment' in message or 'cod' in message or 'ewallet' in message:
        reply = "We currently support Cash on Delivery (COD) and E-Wallet payments. You can choose your preferred method at checkout."
    elif 'sell' in message or 'seller' in message:
        reply = "To start selling, you need a seller account. You can track your sales in the 'My Sales' tab on the seller dashboard."
    elif 'hello' in message or 'hi ' in message or message == 'hi':
        reply = "Hello there! Welcome to the IVS Marketplace. How can I assist you today?"
    else:
        reply = "I'm a simple automated assistant. I can help with questions about orders, payments, addresses, or selling. Can you be more specific?"
        
    return jsonify({'reply': reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
