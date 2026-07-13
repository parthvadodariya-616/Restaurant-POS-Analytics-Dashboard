from flask import Blueprint, render_template, session, redirect, url_for, request
from flask_login import current_user

view_bp = Blueprint('view', __name__)

@view_bp.route('/')
def login_page():
    """Renders the main landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('view.dashboard'))
    return render_template('auth/login.html', title='Welcome')

@view_bp.route('/dashboard')
def dashboard():
    """Renders the main POS dashboard for taking orders."""
    return render_template('dashboard.html', title='Dashboard')

@view_bp.route('/payment')
def payment():
    """Renders the payment processing page."""
    return render_template('payment.html', title='Payment')

@view_bp.route('/admin_panel')
def admin_panel():
    """Renders the admin panel for menu management."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.admin_login_page'))
    return render_template('admin_panel.html', title='Admin Panel')

@view_bp.route('/analytics')
def analytics():
    """Renders the sales analytics page."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.admin_login_page'))
    return render_template('analytics.html', title='Analytics')

@view_bp.route('/theme/<theme>')
def switch_theme(theme):
    """Switches the UI theme between light and dark mode."""
    session['theme'] = theme
    return redirect(request.referrer or url_for('view.login_page'))