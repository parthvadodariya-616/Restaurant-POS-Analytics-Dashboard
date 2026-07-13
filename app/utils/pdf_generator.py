from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.models.models import MenuItem, Customer
import os
from flask import current_app

def generate_invoice(order):
    """Generates a POS-style receipt invoice for a given order."""
    instance_path = current_app.instance_path
    
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        
    bill_path = os.path.join(instance_path, f'invoice_{order.id}.pdf')

    # Small receipt width (~3 inches), fixed height
    receipt_width = 3 * inch
    receipt_height = 11 * inch

    c = canvas.Canvas(bill_path, pagesize=(receipt_width, receipt_height))
    width, height = receipt_width, receipt_height

    # Draw border
    c.setLineWidth(1)
    c.rect(0.2 * inch, 0.2 * inch, width - 0.4 * inch, height - 0.4 * inch)

    y_pos = height - 0.4 * inch

    # --- Header ---
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y_pos, "Restaurant Billing POS")
    y_pos -= 0.2 * inch
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, y_pos, "Analytical Dashboard")
    y_pos -= 0.3 * inch

    # Invoice Info
    c.setFont("Helvetica", 8)
    c.drawString(0.3 * inch, y_pos, f"Invoice: #{order.id}")
    y_pos -= 0.15 * inch
    c.drawString(0.3 * inch, y_pos, f"Date: {order.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    y_pos -= 0.3 * inch

    # Customer Info
    customer = Customer.query.get(order.customer_id)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.3 * inch, y_pos, "Billed To:")
    y_pos -= 0.15 * inch
    c.setFont("Helvetica", 8)
    c.drawString(0.3 * inch, y_pos, customer.name)
    y_pos -= 0.15 * inch
    c.drawString(0.3 * inch, y_pos, f"Phone: {customer.phone}")
    y_pos -= 0.15 * inch
    c.drawString(0.3 * inch, y_pos, f"Order Type: {order.order_type}")
    y_pos -= 0.2 * inch

    # Divider
    c.line(0.3 * inch, y_pos, width - 0.3 * inch, y_pos)
    y_pos -= 0.2 * inch

    # Table Header
    c.setFont("Helvetica-Bold", 8)
    c.drawString(0.3 * inch, y_pos, "Item")
    c.drawRightString(width - 1.5 * inch, y_pos, "Qty")
    c.drawRightString(width - 0.9 * inch, y_pos, "Price")
    c.drawRightString(width - 0.3 * inch, y_pos, "Total")
    y_pos -= 0.15 * inch
    c.line(0.3 * inch, y_pos, width - 0.3 * inch, y_pos)
    y_pos -= 0.15 * inch

    # Table Body
    c.setFont("Helvetica", 8)
    subtotal = 0
    for item in order.items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        item_total = item.quantity * item.price_at_purchase
        subtotal += item_total
        
        c.drawString(0.3 * inch, y_pos, menu_item.name)
        c.drawRightString(width - 1.5 * inch, y_pos, str(item.quantity))
        c.drawRightString(width - 0.9 * inch, y_pos, f"Rs.{item.price_at_purchase:.2f}")
        c.drawRightString(width - 0.3 * inch, y_pos, f"Rs.{item_total:.2f}")
        y_pos -= 0.15 * inch

    # Divider before totals
    y_pos -= 0.1 * inch
    c.line(0.3 * inch, y_pos, width - 0.3 * inch, y_pos)
    y_pos -= 0.2 * inch

    # Totals
    gst = subtotal * 0.05
    total = subtotal + gst
    c.setFont("Helvetica", 8)
    c.drawString(0.3 * inch, y_pos, "Subtotal:")
    c.drawRightString(width - 0.3 * inch, y_pos, f"Rs.{subtotal:.2f}")
    y_pos -= 0.15 * inch

    c.drawString(0.3 * inch, y_pos, "GST (5%):")
    c.drawRightString(width - 0.3 * inch, y_pos, f"Rs.{gst:.2f}")
    y_pos -= 0.15 * inch

    c.setFont("Helvetica-Bold", 9)
    c.drawString(0.3 * inch, y_pos, "TOTAL:")
    c.drawRightString(width - 0.3 * inch, y_pos, f"Rs.{total:.2f}")
    y_pos -= 0.3 * inch

    # Footer
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(width / 2, y_pos, "Thank you for your business!")
    y_pos -= 0.15 * inch
    c.drawCentredString(width / 2, y_pos, "Visit Again!")

    c.save()
