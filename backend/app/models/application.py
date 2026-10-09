from datetime import datetime
from app import db

class Application(db.Model):
    __tablename__ = 'application'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied')  # 'Applied', 'Shortlisted', 'Selected', 'Rejected'
    interview_date = db.Column(db.DateTime)
    interview_location = db.Column(db.String(200))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive_application'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_roll_number': self.student.roll_number if self.student else None,
            'student_branch': self.student.branch if self.student else None,
            'student_cgpa': self.student.cgpa if self.student else None,
            'drive_id': self.drive_id,
            'drive_title': self.drive.job_title if self.drive else None,
            'company_name': self.drive.company.company_name if self.drive and self.drive.company else None,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_location': self.interview_location,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
