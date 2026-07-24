from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
import os, random
from models import db, User, Asset, Transaction, ActivityLog

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    recent_assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).order_by(Asset.created_at.desc()).limit(3).all()
    return render_template('seller/dashboard.html', assets=recent_assets)

@seller_bp.route('/seller/asset/<int:asset_id>')
@login_required
def seller_asset_detail(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("You don't have permission to view this asset.")
        return redirect(url_for('seller.seller_listings'))
        
    mock_views = random.randint(15, 300) 
    return render_template('seller/asset-detail.html', asset=asset, views=mock_views)

@seller_bp.route('/seller/listings')
@login_required
def seller_listings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).all()
    return render_template('seller/listings.html', assets=assets)

@seller_bp.route('/seller/feature-collection/<int:asset_id>', methods=['POST'])
@login_required
def seller_feature_collection(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("Unauthorized")
        return redirect(url_for('seller.seller_listings'))
        
    unfeatured_id = None
    if not asset.is_featured_collection:
        count = Asset.query.filter_by(seller_id=current_user.store_owner_id, is_featured_collection=True).count()
        if count >= 4:
            # Un-feature the oldest featured item (proxy by created_at or id)
            oldest_featured = Asset.query.filter_by(seller_id=current_user.store_owner_id, is_featured_collection=True).order_by(Asset.id.asc()).first()
            if oldest_featured:
                oldest_featured.is_featured_collection = False
                unfeatured_id = oldest_featured.id
        asset.is_featured_collection = True
    else:
        asset.is_featured_collection = False
        
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax'):
        return jsonify({'success': True, 'is_featured': asset.is_featured_collection, 'unfeatured_id': unfeatured_id})
        
    flash('Collection feature status updated.')
    return redirect(url_for('seller.seller_listings'))

@seller_bp.route('/seller/feature-story/<int:asset_id>', methods=['POST'])
@login_required
def seller_feature_story(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("Unauthorized")
        return redirect(url_for('seller.seller_listings'))
        
    if not asset.is_featured_story:
        # If featuring a new one, we could automatically unfeature the old one, but enforcing the limit of 1 is safer.
        # Let's auto-unfeature the old one to make it easier for the seller.
        old_featured = Asset.query.filter_by(seller_id=current_user.store_owner_id, is_featured_story=True).first()
        if old_featured:
            old_featured.is_featured_story = False
        asset.is_featured_story = True
    else:
        asset.is_featured_story = False
        
    db.session.commit()
    flash('Story feature status updated.')
    return redirect(url_for('seller.seller_listings'))

@seller_bp.route('/seller/sales')
@login_required
def seller_sales():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    transactions = Transaction.query.join(Asset).filter(Asset.seller_id == current_user.store_owner_id).order_by(Transaction.date_purchased.desc()).all()
    return render_template('seller/sales.html', transactions=transactions)

@seller_bp.route('/seller/add-asset', methods=['GET', 'POST'])
@login_required
def seller_add_asset():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
        
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
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            image.save(os.path.join(upload_dir, filename))
            
        document = request.files.get('document')
        if document and document.filename:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
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
        return redirect(url_for('seller.seller_listings'))
        
    return render_template('seller/add-asset.html')

@seller_bp.route('/seller/add-employee', methods=['GET', 'POST'])
@login_required
def seller_add_employee():
    if current_user.role != 'seller':
        flash('Only store owners can add employees.')
        return redirect(url_for('seller.seller_dashboard'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('seller.seller_add_employee'))
            
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
        return redirect(url_for('seller.seller_add_employee'))
        
    employees = User.query.filter_by(role='employee', employer_id=current_user.id).all()
    return render_template('seller/add-employee.html', employees=employees)

@seller_bp.route('/seller/edit-employee/<int:id>', methods=['GET', 'POST'])
@login_required
def seller_edit_employee(id):
    if current_user.role != 'seller':
        flash('Only store owners can edit employees.')
        return redirect(url_for('seller.seller_dashboard'))
        
    employee = User.query.get_or_404(id)
    if employee.employer_id != current_user.id:
        flash("You can only edit your own employees.")
        return redirect(url_for('seller.seller_dashboard'))
        
    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        
        new_email = request.form.get('email')
        if new_email != employee.email and User.query.filter_by(email=new_email).first():
            flash('Email already registered.')
            return redirect(url_for('seller.seller_edit_employee', id=id))
        employee.email = new_email
            
        password = request.form.get('password')
        if password:  
            employee.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
        log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.id, action='edit_employee', details=f"Edited employee {employee.first_name} {employee.last_name}")
        db.session.add(log)
        db.session.commit()
        
        flash('Employee updated successfully!')
        return redirect(url_for('seller.seller_add_employee'))
        
    return render_template('seller/edit-employee.html', employee=employee)

@seller_bp.route('/seller/delete-employee/<int:id>', methods=['POST'])
@login_required
def seller_delete_employee(id):
    if current_user.role != 'seller':
        flash('Only store owners can delete employees.')
        return redirect(url_for('seller.seller_dashboard'))
        
    employee = User.query.get_or_404(id)
    if employee.employer_id != current_user.id:
        flash("You can only delete your own employees.")
        return redirect(url_for('seller.seller_dashboard'))
        
    employee_name = f"{employee.first_name} {employee.last_name}"
    
    db.session.delete(employee)
    
    log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.id, action='delete_employee', details=f"Deleted employee {employee_name}")
    db.session.add(log)
    db.session.commit()
    
    flash('Employee account deleted successfully.')
    return redirect(url_for('seller.seller_add_employee'))

@seller_bp.route('/seller/logs')
@login_required
def seller_logs():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    logs = ActivityLog.query.filter_by(store_owner_id=current_user.store_owner_id).order_by(ActivityLog.timestamp.desc()).all()
    return render_template('seller/logs.html', logs=logs)

@seller_bp.route('/seller/analytics')
@login_required
def seller_analytics():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    return render_template('seller/analytics.html')

@seller_bp.route('/seller/settings')
@login_required
def seller_settings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    return render_template('seller/settings.html')
