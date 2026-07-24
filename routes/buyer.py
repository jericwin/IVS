from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Asset, Transaction, Address, ActivityLog, User, CartItem
import os

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


@buyer_bp.route('/buyer/cart', methods=['GET'])
@login_required
def buyer_cart():
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
    
    cart_items = CartItem.query.filter_by(buyer_id=current_user.id).all()
    total_price = sum(item.asset.price * item.quantity for item in cart_items if item.asset.status == 'Active')
    
    return render_template('buyer/cart.html', cart_items=cart_items, total_price=total_price)

@buyer_bp.route('/buyer/cart/add/<int:asset_id>', methods=['POST'])
@login_required
def buyer_cart_add(asset_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
        
    asset = Asset.query.get_or_404(asset_id)
    if asset.status != 'Active':
        flash('This item is no longer available.')
        return redirect(url_for('buyer.buyer_marketplace'))
        
    variation = request.form.get('variation')
    quantity = int(request.form.get('quantity', 1))
    
    # Check if already in cart
    existing_item = CartItem.query.filter_by(buyer_id=current_user.id, asset_id=asset_id, variation=variation).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(buyer_id=current_user.id, asset_id=asset_id, variation=variation, quantity=quantity)
        db.session.add(new_item)
        
    db.session.commit()
    flash('Item added to cart.')
    return redirect(url_for('buyer.buyer_cart'))

@buyer_bp.route('/buyer/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def buyer_cart_remove(item_id):
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
        
    item = CartItem.query.get_or_404(item_id)
    if item.buyer_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart.')
        
    return redirect(url_for('buyer.buyer_cart'))

@buyer_bp.route('/buyer/checkout', methods=['GET', 'POST'])
@login_required
def buyer_checkout():
    if current_user.role != 'buyer':
        return redirect(url_for('seller.seller_dashboard'))
        
    cart_items = CartItem.query.filter_by(buyer_id=current_user.id).all()
    
    # Filter out inactive items
    active_items = [item for item in cart_items if item.asset.status == 'Active']
    
    if not active_items:
        flash('Your cart is empty or items are no longer available.')
        return redirect(url_for('buyer.buyer_marketplace'))
        
    total_price = sum(item.asset.price * item.quantity for item in active_items)
        
    if request.method == 'POST':
        selected_address_id = request.form.get('address_id')
        if not selected_address_id:
            flash('Please select a delivery address.')
            return redirect(url_for('buyer.buyer_checkout'))
            
        payment_method = request.form.get('payment_method', 'Cash on Delivery')
        
        sellers_involved = set()
        
        for item in active_items:
            asset = item.asset
            asset.status = 'Sold'
            transaction = Transaction(
                asset_id=asset.id, 
                buyer_id=current_user.id,
                address_id=selected_address_id,
                payment_method=payment_method,
                variation_name=item.variation
            )
            db.session.add(transaction)
            
            # Log activity for the seller
            log = ActivityLog(
                user_id=asset.seller_id,
                store_owner_id=asset.seller_id,
                action='new_order',
                details=f"Received a new order for {asset.name}"
            )
            db.session.add(log)
            sellers_involved.add(asset.seller_id)
            
            db.session.delete(item) # Remove from cart
            
        db.session.commit()
        
        # Send Email to Sellers
        for seller_id in sellers_involved:
            seller = User.query.get(seller_id)
            if seller:
                sender_email = os.environ.get('MAIL_USERNAME')
                sender_password = os.environ.get('MAIL_PASSWORD')
                
                if sender_email and sender_password:
                    try:
                        import smtplib
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        recipient = os.environ.get('NEW_ORDER_EMAIL', seller.email)
                        msg['To'] = recipient
                        msg['Subject'] = f'New Orders Received'
                        
                        body = f"""Hello {seller.first_name},

You have received new orders!

Please check your 'My Sales' dashboard to view the details.

Thanks,
IVS Team"""
                        msg.attach(MIMEText(body, 'plain'))
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                        server.quit()
                    except Exception as e:
                        print(f"Error sending email to seller: {e}")
        
        flash('Purchase successful! The assets are now in your collection.')
        return redirect(url_for('buyer.buyer_purchases'))
        
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    default_address = next((a for a in addresses if a.is_default), addresses[0] if addresses else None)
    
    return render_template('buyer/checkout.html', cart_items=active_items, total_price=total_price, addresses=addresses, default_address=default_address)

@buyer_bp.route('/buyer/settings')
@login_required
def buyer_settings():
    return render_template('buyer/settings.html')
