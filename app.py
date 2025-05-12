from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
from sqlalchemy import create_engine
import os
from werkzeug.exceptions import HTTPException
import logging

def create_app():
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
    
    # Ensure upload directories exist
    try:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'avatars'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'posts'), exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create upload directories: {str(e)}")
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {str(e)}")
            return None
    
    # Register blueprints
    from routes import blog
    from auth import auth
    
    app.register_blueprint(blog)
    app.register_blueprint(auth)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        logger.error(f"Unhandled exception: {str(e)}")
        return render_template('500.html'), 500
    
    # Create database tables
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 