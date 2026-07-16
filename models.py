from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'buyer' or 'seller'
    assets = db.relationship('Asset', backref='seller', lazy=True)
    purchases = db.relationship('Transaction', backref='buyer', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Sold
    image_filename = db.Column(db.String(100), default='product-1.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction = db.relationship('Transaction', backref='asset', uselist=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    
    address = db.relationship('Address', backref='transactions')
