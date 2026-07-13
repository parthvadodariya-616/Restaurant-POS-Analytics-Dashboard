from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login helper to load a user from the database."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for admin accounts."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')

class MenuItem(db.Model):
    """MenuItem model for all food and beverage items."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    image_path = db.Column(db.String(200), nullable=False, default='default.jpg')

class Customer(db.Model):
    """Customer model to store customer information."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Order(db.Model):
    """Order model to store order details."""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_type = db.Column(db.String(20), nullable=False, default='Dine-In')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    transaction = db.relationship('PaymentTransaction', backref='order', uselist=False, cascade="all, delete-orphan")

class OrderItem(db.Model):
    """OrderItem model to link orders and menu items."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

class PaymentTransaction(db.Model):
    """PaymentTransaction model to log payment details."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), unique=True, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
