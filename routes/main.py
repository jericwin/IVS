from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Address, Asset

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch featured collection assets
    collection_assets = Asset.query.filter_by(status='Active', is_featured_collection=True).order_by(Asset.created_at.desc()).limit(4).all()
    if not collection_assets:
        collection_assets = Asset.query.filter_by(status='Active').order_by(Asset.created_at.desc()).limit(4).all()
    
    # Fetch featured story asset
    story_asset = Asset.query.filter_by(status='Active', is_featured_story=True).order_by(Asset.created_at.desc()).first()
    if not story_asset:
        story_asset = Asset.query.filter_by(status='Active').order_by(Asset.created_at.desc()).first()
    
    return render_template('index.html', collection_assets=collection_assets, story_asset=story_asset)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('main.profile'))
    return render_template('profile.html')

@main_bp.route('/profile/addresses', methods=['GET', 'POST'])
@login_required
def profile_addresses():
    if request.method == 'POST':
        recipient_name = request.form.get('recipient_name')
        phone = request.form.get('phone')
        street_address = request.form.get('street_address')
        
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
        return redirect(url_for('main.profile_addresses'))
        
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('addresses.html', addresses=addresses)

@main_bp.route('/profile/addresses/set_default/<int:address_id>')
@login_required
def set_default_address(address_id):
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    for addr in addresses:
        addr.is_default = False
    
    target = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if target:
        target.is_default = True
        db.session.commit()
        flash('Default address updated.')
    
    return redirect(url_for('main.profile_addresses'))

@main_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    
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
