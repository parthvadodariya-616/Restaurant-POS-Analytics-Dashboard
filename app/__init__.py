import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.admin_login_page'
login_manager.login_message_category = 'info'


def create_app():
    """
    The Application Factory.
    """
    # This simpler initialization allows Flask to automatically
    # find the 'static' and 'templates' folders inside the 'app' directory.
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the configuration from the config.py file
    app.config.from_object('config.Config')

    # Ensure the instance folder exists for the database.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Directory already exists

    # Link the extensions to the Flask app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Import models
        from .models import models
        
        # Import and register Blueprints
        from .routes import view_routes, auth_routes, api_routes
        app.register_blueprint(view_routes.view_bp)
        app.register_blueprint(auth_routes.auth_bp, url_prefix='/auth')
        app.register_blueprint(api_routes.api_bp, url_prefix='/api')
        
        # Create database tables
        db.create_all()
        
        # First-run setup
        if models.User.query.first() is None:
            from .services import initial_setup
            initial_setup.create_default_admin()
            initial_setup.seed_initial_menu()
            
    return app
