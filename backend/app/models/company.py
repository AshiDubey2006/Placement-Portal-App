from datetime import datetime
from app import db


class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(200), nullable=False, index=True)
    hr_contact = db.Column(db.String(100))
    hr_email = db.Column(db.String(120))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    drives = db.relationship('Drive', backref='company', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'hr_contact': self.hr_contact,
            'hr_email': self.hr_email,
            'website': self.website,
            'description': self.description,
            'industry': self.industry,
            'location': self.location,
            'approval_status': self.approval_status,
            # Expose blacklist / active flags from the related User so the
            # frontend can render the correct action button without a
            # separate request.
            'is_blacklisted': self.user.is_blacklisted if self.user else False,
            'is_active': self.user.is_active if self.user else True,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
