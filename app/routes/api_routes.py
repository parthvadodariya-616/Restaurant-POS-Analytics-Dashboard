from flask import Blueprint, jsonify, request, url_for, send_from_directory
from app import db
from app.models.models import MenuItem, Customer, Order, OrderItem, PaymentTransaction
from flask_login import login_required
from app.utils.pdf_generator import generate_invoice
import csv
import io
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

# Public API
@api_bp.route('/menu', methods=['GET'])
def get_menu():
    items = MenuItem.query.filter_by(is_available=True).all()
    menu_list = []
    for item in items:
        menu_list.append({
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'price': item.price,
            'image_path': url_for('static', filename=f'images/menu_items/{item.image_path}')
        })
    return jsonify(menu_list)

@api_bp.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    cart = data.get('cart')
    customer_name = data.get('name')
    customer_phone = data.get('phone')
    order_type = data.get('orderType', 'Dine-In')

    if not all([cart, customer_name, customer_phone]):
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    # Find or create customer
    customer = Customer.query.filter_by(phone=customer_phone).first()
    if not customer:
        customer = Customer(name=customer_name, phone=customer_phone)
        db.session.add(customer)
        db.session.commit()

    # Calculate total and create order
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    gst = total_amount * 0.05
    final_total = total_amount + gst
    
    new_order = Order(
        customer_id=customer.id,
        total_amount=final_total,
        order_type=order_type
    )
    db.session.add(new_order)
    db.session.commit()

    for item in cart:
        menu_item = MenuItem.query.get(item['id'])
        if menu_item:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=menu_item.id,
                quantity=item['quantity'],
                price_at_purchase=menu_item.price
            )
            db.session.add(order_item)
    
    db.session.commit()

    return jsonify({
        'success': True, 
        'order_id': new_order.id,
        'total': new_order.total_amount
    })


@api_bp.route('/order/<int:order_id>/pay', methods=['POST'])
def pay_for_order(order_id):
    data = request.get_json()
    payment_method = data.get('method')
    
    order = Order.query.get_or_404(order_id)
    if order.status == 'paid':
        return jsonify({'success': False, 'message': 'Order already paid'}), 400

    # Create payment transaction
    details = ""
    if payment_method == 'Card':
        card_number = data.get('cardnumber', '')
        details = f"Card ending in {card_number[-4:]}"
    elif payment_method == 'UPI':
        details = f"UPI ID: {data.get('upi_id')}"

    transaction = PaymentTransaction(
        order_id=order.id,
        payment_method=payment_method,
        details=details
    )
    db.session.add(transaction)
    
    # Update order status
    order.status = 'paid'
    db.session.commit()

    # Generate PDF Invoice
    bill_path = generate_invoice(order)
    bill_url = url_for('api.download_invoice', filename=f'invoice_{order.id}.pdf', _external=True)


    return jsonify({
        'success': True, 
        'message': 'Payment successful! Bill generated.',
        'bill_url': bill_url
    })

@api_bp.route('/invoices/<filename>')
def download_invoice(filename):
    return send_from_directory('../instance', filename)


# Admin-Only API
@api_bp.route('/admin/menu', methods=['GET'])
@login_required
def get_admin_menu():
    items = MenuItem.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'price': item.price,
        'is_available': item.is_available
    } for item in items])

@api_bp.route('/admin/menu/upload', methods=['POST'])
@login_required
def upload_menu():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input, None)  # Skip header
        for row in csv_input:
            name, category, price, is_available_str = row
            is_available = is_available_str.lower() in ['true', '1', 'yes']
            
            menu_item = MenuItem.query.filter_by(name=name).first()
            if menu_item:
                menu_item.category = category
                menu_item.price = float(price)
                menu_item.is_available = is_available
            else:
                menu_item = MenuItem(
                    name=name,
                    category=category,
                    price=float(price),
                    is_available=is_available,
                    image_path=f"{name}.jpg" # Assumes image exists
                )
                db.session.add(menu_item)
        db.session.commit()
        return jsonify({'message': 'Menu imported successfully'})
    return jsonify({'error': 'Invalid file type'}), 400


@api_bp.route('/admin/menu/download', methods=['GET'])
@login_required
def download_menu():
    items = MenuItem.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['name', 'category', 'price', 'is_available'])
    for item in items:
        writer.writerow([item.name, item.category, item.price, item.is_available])
    
    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Disposition': 'attachment; filename=menu_export.csv',
        'Content-Type': 'text/csv'
    }
@api_bp.route('/analytics/dashboard', methods=['GET'])
@login_required
def analytics_dashboard():
    range_param = request.args.get('range', '7d')

    if range_param == '1d':
        start_date = datetime.utcnow() - timedelta(days=1)
        group_by_hour = True
    elif range_param == '30d':
        start_date = datetime.utcnow() - timedelta(days=30)
        group_by_hour = False
    else:
        start_date = datetime.utcnow() - timedelta(days=7)
        group_by_hour = False

    total_sales = db.session.query(db.func.sum(Order.total_amount))\
        .filter(Order.status == 'paid', Order.timestamp >= start_date)\
        .scalar() or 0
    total_orders = db.session.query(db.func.count(Order.id))\
        .filter(Order.status == 'paid', Order.timestamp >= start_date)\
        .scalar() or 0
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    labels, data = [], []
    if group_by_hour:
        for hour in range(24):
            start_time = start_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)
            sales_sum = db.session.query(db.func.sum(Order.total_amount)).filter(
                Order.status == 'paid',
                Order.timestamp >= start_time,
                Order.timestamp < end_time
            ).scalar() or 0
            labels.append(start_time.strftime('%H:00'))
            data.append(sales_sum)
    else:
        total_days = int(range_param.replace('d', '')) if range_param.endswith('d') else 7
        today = datetime.utcnow().date()
        for i in range(total_days - 1, -1, -1):
            day = today - timedelta(days=i)
            start_of_day = datetime.combine(day, datetime.min.time())
            end_of_day = datetime.combine(day, datetime.max.time())
            daily_sales = db.session.query(db.func.sum(Order.total_amount)).filter(
                Order.status == 'paid',
                Order.timestamp >= start_of_day,
                Order.timestamp <= end_of_day
            ).scalar() or 0
            labels.append(day.strftime('%b %d'))
            data.append(daily_sales)

    sales_trends = {'labels': labels, 'data': data}

    order_type_results = db.session.query(
        Order.order_type,
        db.func.sum(Order.total_amount)
    ).filter(Order.status == 'paid', Order.timestamp >= start_date)\
     .group_by(Order.order_type).all()
    order_type = {
        'labels': [r[0] for r in order_type_results],
        'values': [float(r[1] or 0) for r in order_type_results]
    }

    payment_results = db.session.query(
        PaymentTransaction.payment_method,
        db.func.sum(Order.total_amount)
    ).join(Order, PaymentTransaction.order_id == Order.id)\
     .filter(Order.status == 'paid', Order.timestamp >= start_date)\
     .group_by(PaymentTransaction.payment_method).all()
    payment_methods = {
        'labels': [r[0] for r in payment_results],
        'values': [float(r[1] or 0) for r in payment_results]
    }

    top_items_results = db.session.query(
        MenuItem.name,
        db.func.sum(OrderItem.quantity)
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status == 'paid', Order.timestamp >= start_date)\
     .group_by(MenuItem.name)\
     .order_by(db.func.sum(OrderItem.quantity).desc())\
     .limit(10).all()
    top_items = {
        'labels': [r[0] for r in top_items_results],
        'values': [int(r[1] or 0) for r in top_items_results]
    }

    all_items_results = db.session.query(
        MenuItem.name,
        db.func.sum(OrderItem.quantity)
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status == 'paid', Order.timestamp >= start_date)\
     .group_by(MenuItem.name)\
     .order_by(db.func.sum(OrderItem.quantity).desc())\
     .all()
    all_items = {
        'labels': [r[0] for r in all_items_results],
        'values': [int(r[1] or 0) for r in all_items_results]
    }

    return jsonify({
        'kpis': {
            'total_sales': float(total_sales),
            'total_orders': total_orders,
            'avg_order_value': float(avg_order_value)
        },
        'sales_trends': sales_trends,
        'order_type': order_type,
        'payment_methods': payment_methods,
        'top_items': top_items,
        'all_items': all_items
    })


@api_bp.route('/analytics/items-sales/export', methods=['GET'])
@login_required
def export_items_sales_csv():
    range_param = request.args.get('range', '7d')

    if range_param == '1d':
        start_date = datetime.utcnow() - timedelta(days=1)
    elif range_param == '30d':
        start_date = datetime.utcnow() - timedelta(days=30)
    else:
        start_date = datetime.utcnow() - timedelta(days=7)

    results = db.session.query(
        MenuItem.name,
        db.func.sum(OrderItem.quantity)
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.status == 'paid', Order.timestamp >= start_date)\
     .group_by(MenuItem.name)\
     .order_by(db.func.sum(OrderItem.quantity).desc())\
     .all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Item Name', 'Quantity Sold'])
    for name, qty in results:
        writer.writerow([name, int(qty or 0)])

    output.seek(0)
    return output.getvalue(), 200, {
        'Content-Disposition': f'attachment; filename=items_sales_{range_param}.csv',
        'Content-Type': 'text/csv'
    }
