from app import db, bcrypt
from app.models.models import User, MenuItem

def create_default_admin():
    """Creates a default admin user if one doesn't exist."""
    if User.query.filter_by(username='admin').first() is None:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(username='admin', password_hash=hashed_password, role='admin')
        db.session.add(admin_user)
        db.session.commit()
        print("--- Default admin user created. Username: 'admin', Password: 'admin123' ---")

def seed_initial_menu():
    """Seeds the database with initial menu items if the table is empty."""
    if MenuItem.query.count() == 0:
        menu_items = [
            MenuItem(name='Margherita Pizza', category='Pizza', price=250.00, image_path='Margherita_Pizza.jpg'),
            MenuItem(name='Pepperoni Feast', category='Pizza', price=350.00, image_path='Pepperoni_Feast.jpg'),
            MenuItem(name='Classic Veg Burger', category='Burger', price=150.00, image_path='Classic_Veg_Burger.jpg'),
            MenuItem(name='Spicy Chicken Burger', category='Burger', price=200.00, image_path='Spicy_Chicken_Burger.jpg'),
            MenuItem(name='Cheesy Garlic Bread', category='Sides', price=120.00, image_path='Cheesy_Garlic_Bread.jpg'),
            MenuItem(name='Coca-Cola', category='Beverages', price=40.00, image_path='Coca-Cola.jpg'),
            MenuItem(name='Fresh Lime Soda', category='Beverages', price=60.00, image_path='Fresh_Lime_Soda.jpg'),
        ]
        db.session.bulk_save_objects(menu_items)
        db.session.commit()
        print("--- Initial menu items have been seeded into the database. ---")