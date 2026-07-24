from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Asset, Transaction, Address

buyer_bp = Blueprint('buyer', __name__)

@buyer_bp.route('/buyer/dashboard')
@login_required
def buyer_dashboard():
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
    recent_assets = Asset.query.filter_by(status='Active').order_by(Asset.created_at.desc()).limit(3).all()
    return render_template('buyer/dashboard.html', assets=recent_assets)

@buyer_bp.route('/buyer/marketplace')
@login_required
def buyer_marketplace():
    assets = Asset.query.filter_by(status='Active').order_by(Asset.created_at.desc()).all()
    return render_template('buyer/marketplace.html', assets=assets)

@buyer_bp.route('/buyer/purchases')
@login_required
def buyer_purchases():
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
    transactions = Transaction.query.filter_by(buyer_id=current_user.id).order_by(Transaction.date_purchased.desc()).all()
    return render_template('buyer/purchases.html', transactions=transactions)

@buyer_bp.route('/buyer/asset/<int:asset_id>')
@login_required
def buyer_asset_detail(asset_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
    asset = Asset.query.get_or_404(asset_id)
    
    asset.views = (asset.views or 0) + 1
    db.session.commit()
    
    return render_template('buyer/asset-detail.html', asset=asset)

@buyer_bp.route('/buyer/checkout/<int:asset_id>', methods=['GET', 'POST'])
@login_required
def buyer_checkout(asset_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
    
    asset = Asset.query.get_or_404(asset_id)
    if asset.status != 'Active':
        flash('This item is no longer available.')
        return redirect(url_for('buyer.buyer_dashboard'))
        
    if request.method == 'POST':
        selected_address_id = request.form.get('address_id')
        if not selected_address_id:
            flash('Please select a delivery address.')
            return redirect(url_for('buyer.buyer_checkout', asset_id=asset_id))
            
        payment_method = request.form.get('payment_method')
        variation = request.form.get('variation')
        asset.status = 'Sold'
        transaction = Transaction(
            asset_id=asset.id, 
            buyer_id=current_user.id,
            address_id=selected_address_id,
            payment_method=payment_method,
            variation_name=variation
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash('Purchase successful! The asset is now in your collection.')
        return redirect(url_for('buyer.buyer_dashboard'))
        
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    default_address = next((a for a in addresses if a.is_default), addresses[0] if addresses else None)
    
    variation = request.args.get('variation')
    
    return render_template('buyer/checkout.html', asset=asset, addresses=addresses, default_address=default_address, variation=variation)

@buyer_bp.route('/buyer/settings')
@login_required
def buyer_settings():
    return render_template('buyer/settings.html')
