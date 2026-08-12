from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import os, smtplib, random
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import db, User, ActivityLog
from routes import oauth  # We'll initialize OAuth centrally or in app.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            
            if user.role in ['seller', 'employee']:
                log = ActivityLog(user_id=user.id, store_owner_id=user.store_owner_id, action='login', details=f"Logged in via IP {request.remote_addr}")
                db.session.add(log)
                db.session.commit()
                
            if user.role == 'buyer':
                return redirect(url_for('buyer.buyer_marketplace'))
            else:
                return redirect(url_for('seller.seller_dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.signup'))
            
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
        return redirect(url_for('auth.login'))
            
    return render_template('signup.html')

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, prompt='select_account')

@auth_bp.route('/authorize/google')
def authorize_google():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    
    email = user_info.get('email')
    first_name = user_info.get('given_name', 'Google')
    last_name = user_info.get('family_name', 'User')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        # Create user if it doesn't exist
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash('google_auth_placeholder', method='pbkdf2:sha256'),
            role='buyer'
        )
        db.session.add(user)
        db.session.commit()
        
    login_user(user)
    
    if user.role in ['seller', 'employee']:
        log = ActivityLog(user_id=user.id, store_owner_id=user.store_owner_id, action='login', details=f"Logged in via Google IP {request.remote_addr}")
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('seller.seller_dashboard'))
        
    return redirect(url_for('buyer.buyer_marketplace'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email_addr = request.form.get('email')
        user = User.query.filter_by(email=email_addr).first()
        
        if user:
            # Generate code
            code = str(random.randint(100000, 999999))
            user.reset_code = code
            user.reset_code_expiration = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            
            # Send Email
            sender_email = os.environ.get('MAIL_USERNAME')
            sender_password = os.environ.get('MAIL_PASSWORD')
            
            if sender_email and sender_password:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = user.email
                    msg['Subject'] = 'Your IVS Password Reset Code'
                    
                    body = f"Hello {user.first_name},\n\nYour password reset code is: {code}\n\nThis code will expire in 15 minutes.\n\nThanks,\nIVS Team"
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    
                    flash('Verification code sent to your email.')
                    return render_template('verify_reset_code.html', email=user.email)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    flash('Error sending email. Please try again later.')
            else:
                print(f"DEBUG: Reset code for {user.email} is {code}")
                flash('Email credentials not configured. Code printed to console for debugging.')
                return render_template('verify_reset_code.html', email=user.email)
                
        else:
            flash('If an account with that email exists, a verification code has been sent.')
            return render_template('verify_reset_code.html', email=email_addr)
            
    return render_template('forgot_password.html')

@auth_bp.route('/verify-reset-code', methods=['POST'])
def verify_reset_code():
    email_addr = request.form.get('email')
    code = request.form.get('code')
    new_password = request.form.get('new_password')
    
    user = User.query.filter_by(email=email_addr).first()
    
    if user and user.reset_code == code:
        if user.reset_code_expiration and user.reset_code_expiration > datetime.utcnow():
            user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            user.reset_code = None
            user.reset_code_expiration = None
            db.session.commit()
            flash('Password reset successfully! Please log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Verification code has expired. Please request a new one.')
            return render_template('verify_reset_code.html', email=email_addr)
    else:
        flash('Invalid verification code.')
        return render_template('verify_reset_code.html', email=email_addr)

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.role in ['seller', 'employee']:
        log = ActivityLog(user_id=current_user.id, store_owner_id=current_user.store_owner_id, action='logout', details="Logged out")
        db.session.add(log)
        db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))
