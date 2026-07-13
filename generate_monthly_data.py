import sys
import os
import random
from datetime import datetime, timedelta

# This allows Python to find the 'app' directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.models import MenuItem, Customer, Order, OrderItem, PaymentTransaction

def generate_historical_sales_data():
    """
    Generates two years of realistic, random sales data and saves it to the database.
    """
    app = create_app()
    with app.app_context():
        print("--- Starting to generate TWO YEARS of sales data. This might take a few minutes... ---")

        menu_items = MenuItem.query.all()
        if not menu_items:
            print("!!! Error: No menu items found in the database. Please seed the menu first. !!!")
            return

        # Generate data for the last 730 days (2 years)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        current_date = start_date
        
        total_orders_created = 0

        while current_date <= end_date:
            # Create a random number of orders for the current day
            num_orders_today = random.randint(20, 60) 
            
            for _ in range(num_orders_today):
                customer_phone = f"98765{random.randint(10000, 99999)}"
                customer = Customer.query.filter_by(phone=customer_phone).first()
                if not customer:
                    customer = Customer(name=f"Customer {random.randint(1, 1000)}", phone=customer_phone)
                    db.session.add(customer)
                    db.session.commit()

                order_timestamp = current_date.replace(
                    hour=random.randint(9, 22), 
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                new_order = Order(
                    customer_id=customer.id,
                    status='paid',
                    total_amount=0, 
                    order_type=random.choice(['Dine-In', 'Takeaway', 'Delivery']),
                    timestamp=order_timestamp
                )
                db.session.add(new_order)
                db.session.commit()

                order_total = 0
                num_items_in_order = random.randint(1, 5)
                for _ in range(num_items_in_order):
                    menu_item = random.choice(menu_items)
                    quantity = random.randint(1, 3)
                    item_total = menu_item.price * quantity
                    order_total += item_total
                    
                    order_item = OrderItem(
                        order_id=new_order.id,
                        menu_item_id=menu_item.id,
                        quantity=quantity,
                        price_at_purchase=menu_item.price
                    )
                    db.session.add(order_item)

                gst = order_total * 0.05
                final_total = order_total + gst
                new_order.total_amount = final_total
                
                transaction = PaymentTransaction(
                    order_id=new_order.id,
                    payment_method=random.choice(['Card', 'UPI', 'Cash']),
                    details="Automated historical generation"
                )
                db.session.add(transaction)
                db.session.commit()
                total_orders_created += 1

            current_date += timedelta(days=1)

        print(f"--- Successfully created {total_orders_created} orders over the past two years. ---")

if __name__ == '__main__':
    generate_historical_sales_data()