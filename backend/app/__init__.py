from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from flask_mail import Mail
from config import Config
import os

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialise extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.company import company_bp
    from app.routes.student import student_bp
    from app.routes.drive import drive_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(drive_bp, url_prefix='/api/drive')

    # Create tables and seed admin user on first run
    with app.app_context():
        db.create_all()
        from app.utils.init_db import create_admin_user
        create_admin_user()

    return app
