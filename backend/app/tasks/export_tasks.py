from app.tasks.celery_config import celery_app
import csv
import os
from datetime import datetime


@celery_app.task(name='app.tasks.export_tasks.export_applications_csv')
def export_applications_csv(student_id):
    """Export a student's application history to CSV (async job)."""
    # Import create_app lazily to avoid circular imports at module load time
    from app import create_app
    flask_app = create_app()

    with flask_app.app_context():
        from app.models.student import Student
        from app.models.application import Application

        student = Student.query.get(student_id)
        if not student:
            return None

        applications = Application.query.filter_by(student_id=student_id).all()

        filename = f"applications_{student_id}_{int(datetime.utcnow().timestamp())}.csv"
        filepath = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Student ID', 'Student Name', 'Roll Number',
                'Company Name', 'Drive Title', 'Application Status',
                'Application Date', 'Interview Date', 'Remarks'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for rec in applications:
                writer.writerow({
                    'Student ID': rec.student_id,
                    'Student Name': rec.student.full_name if rec.student else '',
                    'Roll Number': rec.student.roll_number if rec.student else '',
                    'Company Name': (
                        rec.drive.company.company_name
                        if rec.drive and rec.drive.company else ''
                    ),
                    'Drive Title': rec.drive.job_title if rec.drive else '',
                    'Application Status': rec.status,
                    'Application Date': (
                        rec.application_date.isoformat() if rec.application_date else ''
                    ),
                    'Interview Date': (
                        rec.interview_date.isoformat() if rec.interview_date else ''
                    ),
                    'Remarks': rec.remarks or ''
                })

        return filename
