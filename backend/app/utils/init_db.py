from app import db
from app.models.user import User
from app.models.company import Company
from app.models.student import Student

def create_admin_user():
    """Create the default admin user if it doesn't exist"""
    admin = User.query.filter_by(email='admin@placementportal.com').first()
    if not admin:
        admin = User(
            email='admin@placementportal.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')  # Default password, should be changed in production
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        print("Admin user already exists")
