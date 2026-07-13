from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def admin_login_page():
    """Serves the HTML page for the admin login form."""
    if current_user.is_authenticated:
        return redirect(url_for('view.admin_panel'))
    return render_template('auth/admin_login.html', title='Admin Login')

@auth_bp.route('/api/admin/login', methods=['POST'])
def login():
    """API endpoint to handle admin login."""
    if current_user.is_authenticated:
        return jsonify({'success': True, 'redirect_url': url_for('view.admin_panel')})
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'success': True, 'redirect_url': url_for('view.admin_panel')})
    else:
        return jsonify({'success': False, 'message': 'Login Unsuccessful. Please check username and password'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    """Logs the current admin user out."""
    logout_user()
    return redirect(url_for('view.login_page'))