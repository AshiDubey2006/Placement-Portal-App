from datetime import datetime
from app import db

class Drive(db.Model):
    __tablename__ = 'drive'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(200), nullable=False, index=True)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_branch = db.Column(db.String(200))  # Comma-separated branches
    min_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.String(50))  # Comma-separated years
    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    salary_package = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Approved', 'Closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')
    
    def is_eligible(self, student):
        """Check if student is eligible for this drive"""
        # Check CGPA
        if student.cgpa < self.min_cgpa:
            return False
        
        # Check branch
        if self.eligibility_branch:
            eligible_branches = [b.strip().lower() for b in self.eligibility_branch.split(',')]
            if student.branch.lower() not in eligible_branches:
                return False
        
        # Check year
        if self.eligibility_year:
            eligible_years = [y.strip() for y in self.eligibility_year.split(',')]
            if str(student.year) not in eligible_years:
                return False
        
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company.company_name if self.company else None,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'eligibility_branch': self.eligibility_branch,
            'min_cgpa': self.min_cgpa,
            'eligibility_year': self.eligibility_year,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'drive_date': self.drive_date.isoformat() if self.drive_date else None,
            'location': self.location,
            'salary_package': self.salary_package,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'applicant_count': len(self.applications) if self.applications else 0
        }
