from datetime import datetime
from app import db


class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)   # 1-4
    cgpa = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(20))
    resume_path = db.Column(db.String(255))
    skills = db.Column(db.Text)   # comma-separated or JSON string

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship(
        'Application', backref='student', lazy=True, cascade='all, delete-orphan'
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'roll_number': self.roll_number,
            'branch': self.branch,
            'year': self.year,
            'cgpa': self.cgpa,
            'phone': self.phone,
            'resume_path': self.resume_path,
            'skills': self.skills,
            # Expose from User so the admin table can show the right button
            'is_blacklisted': self.user.is_blacklisted if self.user else False,
            'is_active': self.user.is_active if self.user else True,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
