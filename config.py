import os

# Get the absolute path of the directory where this file is located.
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Configuration class for the Flask application.
    """
    # Using a static, non-secret key as requested.
    SECRET_KEY = 'a-simple-static-key-for-dev'
    
    # This is the corrected, more robust path for the database.
    # It will place the database in a folder named 'instance' in your project root.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'restaurant.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
