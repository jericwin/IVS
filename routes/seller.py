from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user
import os, random
from models import db, User, Asset, Transaction, ActivityLog

try:
    from app import csrf
except ImportError:
    csrf = None

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/seller/dashboard')
@login_required
def seller_dashboard():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
        
    assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).order_by(Asset.created_at.desc()).all()
    recent_assets = assets[:3]
    
    total_listed_assets = len(assets)
    store_views = sum((a.views or 0) for a in assets)
    
    asset_ids = [a.id for a in assets]
    transactions = Transaction.query.filter(Transaction.asset_id.in_(asset_ids)).all() if asset_ids else []
    total_sales_volume = sum((tx.asset.price or 0.0) for tx in transactions if tx.asset)
    
    recent_activity = ActivityLog.query.options(db.joinedload(ActivityLog.user)).filter(
        ActivityLog.store_owner_id == current_user.store_owner_id,
        ActivityLog.action.notin_(['login', 'logout'])
    ).order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    return render_template('seller/dashboard.html', 
                           assets=recent_assets,
                           total_listed_assets=total_listed_assets,
                           store_views=store_views,
                           total_sales_volume=total_sales_volume,
                           recent_activity=recent_activity)

@seller_bp.route('/seller/asset/<int:asset_id>')
@login_required
def seller_asset_detail(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("You don't have permission to view this asset.")
        return redirect(url_for('seller.seller_listings'))
        
    return render_template('seller/asset-detail.html', asset=asset, views=asset.views)

@seller_bp.route('/seller/listings')
@login_required
def seller_listings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).order_by(Asset.created_at.desc()).all()
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

from flask import make_response

@seller_bp.route('/seller/sales')
@login_required
def seller_sales():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    transactions = Transaction.query.options(db.joinedload(Transaction.asset), db.joinedload(Transaction.buyer)).join(Asset).filter(Asset.seller_id == current_user.store_owner_id).order_by(Transaction.date_purchased.desc()).all()
    
    resp = make_response(render_template('seller/sales.html', transactions=transactions))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

import uuid
from werkzeug.utils import secure_filename
import requests

def upload_to_catbox(file):
    try:
        # Seek to beginning in case it was read before
        file.stream.seek(0)
        files = {'fileToUpload': (file.filename, file.stream, file.mimetype)}
        data = {'reqtype': 'fileupload'}
        resp = requests.post('https://catbox.moe/user/api.php', files=files, data=data, timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        print(f"Catbox upload error: {e}")
    return None

@seller_bp.route('/seller/sales/update_status/<int:transaction_id>', methods=['POST'])
@csrf.exempt if csrf else lambda f: f
@login_required
def update_delivery_status(transaction_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    
    tx = Transaction.query.get_or_404(transaction_id)
    if tx.asset.seller_id != current_user.store_owner_id:
        flash("Unauthorized")
        return redirect(url_for('seller.seller_sales'))
        
    status = request.form.get('delivery_status')
    if status == 'To be delivered':
        tx.delivery_status = status
        
        log = ActivityLog(
            user_id=current_user.id,
            store_owner_id=current_user.store_owner_id,
            action='update_status',
            details=f"Marked order for {tx.asset.name} as To be delivered"
        )
        db.session.add(log)
        
        db.session.commit()
        flash('Order marked as To be delivered.')
        
    elif status == 'Delivered':
        if 'evidence_image' not in request.files:
            flash('Evidence image is required for Delivered status.')
            return redirect(url_for('seller.seller_sales'))
            
        file = request.files['evidence_image']
        if file.filename == '':
            flash('No image selected.')
            return redirect(url_for('seller.seller_sales'))
            
        if file:
            catbox_url = upload_to_catbox(file)
            if catbox_url:
                tx.delivery_evidence_filename = catbox_url
            else:
                tx.delivery_evidence_filename = "upload_failed.png"
            tx.delivery_status = status
            
            log = ActivityLog(
                user_id=current_user.id,
                store_owner_id=current_user.store_owner_id,
                action='update_status',
                details=f"Marked order for {tx.asset.name} as Delivered"
            )
            db.session.add(log)
            
            db.session.commit()
            flash('Order marked as Delivered with evidence.')
            
    return redirect(url_for('seller.seller_sales'))

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
        
        try:
            parsed_price = float(price) if price else 0.0
        except ValueError:
            parsed_price = 0.0
            
        try:
            parsed_stock = int(stock) if stock else 1
        except ValueError:
            parsed_stock = 1
        
        from models import AssetVariation
        
        # We will keep image_filename as the main image, taking the first variation's image
        # or defaulting to product-1.png if none provided.
        main_image_filename = 'product-1.png'
        
        variation_names = request.form.getlist('variation_name[]')
        variation_images = request.files.getlist('variation_image[]')
        
        # We need to process variations after creating the asset to get the asset ID
        new_asset = Asset(
            name=name,
            price=parsed_price,
            stock=parsed_stock,
            category=category,
            description=description,
            seller_id=current_user.store_owner_id,
            image_filename=main_image_filename
        )
        db.session.add(new_asset)
        db.session.flush() # To get new_asset.id
        
        has_main_image = False
        
        for i in range(len(variation_names)):
            var_name = variation_names[i]
            var_image = variation_images[i] if i < len(variation_images) else None
            
            var_filename = 'product-1.png'
            if var_image and var_image.filename:
                catbox_url = upload_to_catbox(var_image)
                if catbox_url:
                    var_filename = catbox_url
                
            if not has_main_image and var_filename != 'product-1.png':
                new_asset.image_filename = var_filename
                has_main_image = True
                
            new_var = AssetVariation(
                asset_id=new_asset.id,
                name=var_name or f"Variation {i+1}",
                image_filename=var_filename
            )
            db.session.add(new_var)
            
        # If no variations were submitted, create a default one
        if len(variation_names) == 0:
            image = request.files.get('image') # Fallback to old image input if exists
            filename = 'product-1.png'
            if image and image.filename:
                catbox_url = upload_to_catbox(image)
                if catbox_url:
                    filename = catbox_url
                new_asset.image_filename = filename
            new_var = AssetVariation(asset_id=new_asset.id, name="Default", image_filename=filename)
            db.session.add(new_var)

        # Log activity
        log = ActivityLog(
            user_id=current_user.id,
            store_owner_id=current_user.store_owner_id,
            action='add_asset',
            details=f"Added new asset: {new_asset.name}"
        )
        db.session.add(log)

        db.session.commit()
        
        flash('Asset posted successfully!')
        return redirect(url_for('seller.seller_listings'))
        
    return render_template('seller/add-asset.html')

@seller_bp.route('/seller/edit-asset/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def seller_edit_asset(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
        
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("You don't have permission to edit this asset.")
        return redirect(url_for('seller.seller_listings'))
        
    if request.method == 'POST':
        asset.name = request.form.get('name')
        try:
            asset.price = float(request.form.get('price')) if request.form.get('price') else 0.0
        except ValueError:
            pass
        try:
            asset.stock = int(request.form.get('stock')) if request.form.get('stock') else 1
        except ValueError:
            pass
        asset.category = request.form.get('category')
        asset.description = request.form.get('description')
        
        from models import AssetVariation
        
        variation_names = request.form.getlist('variation_name[]')
        variation_images = request.files.getlist('variation_image[]')
        existing_variation_ids = request.form.getlist('existing_variation_id[]')
        
        if len(variation_names) > 0:
            # Delete old variations
            AssetVariation.query.filter_by(asset_id=asset.id).delete()
            
            has_main_image = False
            for i in range(len(variation_names)):
                var_name = variation_names[i]
                var_image = variation_images[i] if i < len(variation_images) else None
                
                # Check if there's an existing image to keep
                existing_img = request.form.get(f'existing_image_{i}')
                var_filename = existing_img or 'product-1.png'
                
                if var_image and var_image.filename:
                    catbox_url = upload_to_catbox(var_image)
                    if catbox_url:
                        var_filename = catbox_url
                    
                if not has_main_image and var_filename != 'product-1.png':
                    asset.image_filename = var_filename
                    has_main_image = True
                    
                new_var = AssetVariation(
                    asset_id=asset.id,
                    name=var_name or f"Variation {i+1}",
                    image_filename=var_filename
                )
                db.session.add(new_var)
        else:
            image = request.files.get('image')
            if image and image.filename:
                catbox_url = upload_to_catbox(image)
                if catbox_url:
                    asset.image_filename = catbox_url
                    
                    # Update default variation image if no variations were passed
                    default_var = AssetVariation.query.filter_by(asset_id=asset.id).first()
                    if default_var:
                        default_var.image_filename = catbox_url
                    else:
                        new_var = AssetVariation(asset_id=asset.id, name="Default", image_filename=catbox_url)
                        db.session.add(new_var)
                
        # Log activity
        log = ActivityLog(
            user_id=current_user.id,
            store_owner_id=current_user.store_owner_id,
            action='edit_asset',
            details=f"Updated asset: {asset.name}"
        )
        db.session.add(log)

        db.session.commit()
        flash('Asset updated successfully!')
        return redirect(url_for('seller.seller_asset_detail', asset_id=asset.id))
        
    return render_template('seller/edit-asset.html', asset=asset)

@seller_bp.route('/seller/delete-asset/<int:asset_id>', methods=['POST'])
@login_required
def seller_delete_asset(asset_id):
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
        
    asset = Asset.query.get_or_404(asset_id)
    if asset.seller_id != current_user.store_owner_id:
        flash("You don't have permission to delete this asset.")
        return redirect(url_for('seller.seller_listings'))
        
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully!')
    return redirect(url_for('seller.seller_listings'))

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
    logs = ActivityLog.query.options(db.joinedload(ActivityLog.user)).filter_by(store_owner_id=current_user.store_owner_id).order_by(ActivityLog.timestamp.desc()).all()
    return render_template('seller/logs.html', logs=logs)

@seller_bp.route('/seller/analytics')
@login_required
def seller_analytics():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
        
    assets = Asset.query.filter_by(seller_id=current_user.store_owner_id).all()
    store_views = sum((a.views or 0) for a in assets)
    
    asset_ids = [a.id for a in assets]
    transactions = Transaction.query.filter(Transaction.asset_id.in_(asset_ids)).all() if asset_ids else []
    total_revenue = sum((tx.asset.price or 0.0) for tx in transactions if tx.asset)
    
    conversion_rate = (len(transactions) / store_views * 100) if store_views > 0 else 0.0
    
    import json
    chart_data = []
    for tx in transactions:
        if tx.asset:
            chart_data.append({
                'date': tx.date_purchased.strftime('%Y-%m-%d'),
                'revenue': float(tx.asset.price or 0.0)
            })
    
    return render_template('seller/analytics.html',
                           total_revenue=total_revenue,
                           store_views=store_views,
                           conversion_rate=conversion_rate,
                           chart_data_json=json.dumps(chart_data))

@seller_bp.route('/seller/settings')
@login_required
def seller_settings():
    if current_user.role not in ['seller', 'employee']:
        return redirect(url_for('buyer.buyer_dashboard'))
    return render_template('seller/settings.html')
