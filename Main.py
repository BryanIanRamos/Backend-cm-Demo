from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from models.db_models import db
from routes.accounts import accounts_bp
from routes.date_created import date_created_bp
from routes.post_data import post_data_bp
from routes.posts import posts_bp
from routes.auth import auth_bp
# asdasd
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initializing database
    db.init_app(app)
    
    # Initialize CSRF protection conditionally
    if Config.CSRF_ENABLED:
        csrf = CSRFProtect(app)
    else:
        csrf = None

    # Create tables if not already created (for development purposes)
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(date_created_bp, url_prefix='/created', name='date_created_blueprint')
    app.register_blueprint(accounts_bp, url_prefix='/accounts', name='accounts_blueprint')
    app.register_blueprint(post_data_bp, url_prefix='/documents', name='post_data_blueprint')
    app.register_blueprint(posts_bp, url_prefix='/posts', name='posts_blueprint')
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Register auth blueprint

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # Set debug=True for development mode
