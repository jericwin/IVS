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
        province = request.form.get('province')
        city = request.form.get('city')
        barangay = request.form.get('barangay')
        street = request.form.get('street')
        house_number = request.form.get('house_number')
        zipcode = request.form.get('zipcode')
        
        street_address = f"{house_number} {street}, {barangay}, {city}, {province} {zipcode}"
        
        existing = Address.query.filter_by(user_id=current_user.id).count()
        is_default = (existing == 0)

        addr = Address(
            user_id=current_user.id,
            recipient_name=recipient_name,
            phone=phone,
            province=province,
            city=city,
            barangay=barangay,
            street=street,
            house_number=house_number,
            zipcode=zipcode,
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


import random, smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash

@main_bp.route('/profile/change-password/request-otp', methods=['POST'])
@login_required
def request_otp():
    code = str(random.randint(100000, 999999))
    current_user.reset_code = code
    current_user.reset_code_expiration = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    sender_email = os.environ.get('MAIL_USERNAME')
    sender_password = os.environ.get('MAIL_PASSWORD')
    
    if sender_email and sender_password:
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = current_user.email
            msg['Subject'] = 'Your Password Change OTP'
            body = f'Hello {current_user.first_name},\n\nYour OTP to change your password is: {code}\n\nThis code will expire in 10 minutes.'
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            return jsonify({'success': True, 'message': 'OTP sent to your email.'})
        except Exception as e:
            print(f'Error sending email: {e}')
            return jsonify({'success': False, 'message': 'Failed to send OTP.'}), 500
    return jsonify({'success': False, 'message': 'Email not configured.'}), 500

@main_bp.route('/profile/change-password/verify', methods=['POST'])
@login_required
def verify_otp():
    otp = request.form.get('otp')
    new_password = request.form.get('new_password')
    
    if not otp or not new_password:
        return jsonify({'success': False, 'message': 'Missing fields.'}), 400
        
    if current_user.reset_code != otp:
        return jsonify({'success': False, 'message': 'Invalid OTP.'}), 400
        
    if not current_user.reset_code_expiration or current_user.reset_code_expiration < datetime.utcnow():
        return jsonify({'success': False, 'message': 'OTP has expired.'}), 400
        
    # Update password
    current_user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    current_user.reset_code = None
    current_user.reset_code_expiration = None
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully.'})
