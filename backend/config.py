import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///placement_portal.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Redis / Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Flask-Caching — use SimpleCache (in-memory) when Redis is not available.
    # Switch to 'RedisCache' and set CACHE_REDIS_URL when Redis is running.
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'SimpleCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300

    # Flask-Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@placementportal.com'
    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get('GOOGLE_CHAT_WEBHOOK_URL')
