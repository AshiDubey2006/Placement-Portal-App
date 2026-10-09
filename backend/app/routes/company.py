from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app import db, cache
from app.models.user import User
from app.models.company import Company
from app.models.drive import Drive
from app.models.application import Application
from app.models.student import Student
from app.utils.decorators import role_required, get_current_user_id
from datetime import datetime
import os

company_bp = Blueprint('company', __name__)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@company_bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required('company')
def get_company_profile():
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    return jsonify(company.to_dict()), 200


@company_bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required('company')
def update_company_profile():
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    data = request.get_json() or {}
    for field in ('company_name', 'hr_contact', 'hr_email', 'website',
                  'description', 'industry', 'location'):
        if field in data:
            setattr(company, field, data[field])

    try:
        db.session.commit()
        cache.delete(f'company_{company.id}')
        return jsonify({'message': 'Profile updated successfully',
                        'company': company.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@company_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('company')
def company_dashboard():
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drives = Drive.query.filter_by(company_id=company.id).all()
    total_applicants = sum(len(d.applications) for d in drives)

    drive_stats = [
        {
            'drive_id': d.id,
            'job_title': d.job_title,
            'status': d.status,
            'applicant_count': len(d.applications),
            'application_deadline': d.application_deadline.isoformat()
            if d.application_deadline else None,
        }
        for d in drives
    ]

    return jsonify({
        'company': company.to_dict(),
        'total_drives': len(drives),
        'total_applicants': total_applicants,
        'drive_stats': drive_stats,
    }), 200


# ---------------------------------------------------------------------------
# Drives
# ---------------------------------------------------------------------------

@company_bp.route('/drives', methods=['POST'])
@jwt_required()
@role_required('company')
def create_drive():
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    if company.approval_status != 'Approved':
        return jsonify({'error': 'Company must be approved before creating drives'}), 403

    data = request.get_json() or {}
    for field in ('job_title', 'job_description', 'application_deadline'):
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        deadline = datetime.fromisoformat(
            data['application_deadline'].replace('Z', '+00:00')
        ).replace(tzinfo=None)
    except ValueError:
        return jsonify({'error': 'Invalid deadline format. Use ISO 8601.'}), 400

    drive_date = None
    if data.get('drive_date'):
        try:
            drive_date = datetime.fromisoformat(
                data['drive_date'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
        except ValueError:
            return jsonify({'error': 'Invalid drive_date format.'}), 400

    drive = Drive(
        company_id=company.id,
        job_title=data['job_title'],
        job_description=data['job_description'],
        eligibility_branch=data.get('eligibility_branch', ''),
        min_cgpa=float(data.get('min_cgpa', 0.0)),
        eligibility_year=data.get('eligibility_year', ''),
        application_deadline=deadline,
        drive_date=drive_date,
        location=data.get('location', ''),
        salary_package=data.get('salary_package', ''),
        status='Pending',
    )

    try:
        db.session.add(drive)
        db.session.commit()
        return jsonify({'message': 'Drive created and pending admin approval',
                        'drive': drive.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives', methods=['GET'])
@jwt_required()
@role_required('company')
def get_company_drives():
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404
    drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.created_at.desc()).all()
    return jsonify({'drives': [d.to_dict() for d in drives]}), 200


@company_bp.route('/drives/<int:drive_id>', methods=['PUT'])
@jwt_required()
@role_required('company')
def update_drive(drive_id):
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404

    # Only allow editing Pending drives
    if drive.status == 'Approved':
        return jsonify({'error': 'Approved drives cannot be edited'}), 403

    data = request.get_json() or {}
    for field in ('job_title', 'job_description', 'eligibility_branch',
                  'eligibility_year', 'location', 'salary_package'):
        if field in data:
            setattr(drive, field, data[field])
    if 'min_cgpa' in data:
        drive.min_cgpa = float(data['min_cgpa'])
    if 'application_deadline' in data and data['application_deadline']:
        try:
            drive.application_deadline = datetime.fromisoformat(
                data['application_deadline'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
        except ValueError:
            return jsonify({'error': 'Invalid deadline format'}), 400
    if 'drive_date' in data:
        if data['drive_date']:
            try:
                drive.drive_date = datetime.fromisoformat(
                    data['drive_date'].replace('Z', '+00:00')
                ).replace(tzinfo=None)
            except ValueError:
                return jsonify({'error': 'Invalid drive_date format'}), 400
        else:
            drive.drive_date = None

    try:
        db.session.commit()
        cache.delete(f'drive_{drive_id}')
        return jsonify({'message': 'Drive updated successfully',
                        'drive': drive.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives/<int:drive_id>/close', methods=['PUT'])
@jwt_required()
@role_required('company')
def close_drive(drive_id):
    """Close a placement drive (change status to Closed)"""
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404

    if drive.status == 'Closed':
        return jsonify({'error': 'Drive is already closed'}), 400

    drive.status = 'Closed'
    try:
        db.session.commit()
        cache.delete(f'drive_{drive_id}')
        return jsonify({'message': 'Drive closed successfully',
                        'drive': drive.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@company_bp.route('/drives/<int:drive_id>', methods=['DELETE'])
@jwt_required()
@role_required('company')
def delete_drive(drive_id):
    """Delete a placement drive"""
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404

    # Only allow deleting Pending drives
    if drive.status == 'Approved':
        return jsonify({'error': 'Approved drives cannot be deleted. Close them instead.'}), 403

    try:
        # Delete all applications for this drive first
        Application.query.filter_by(drive_id=drive_id).delete()
        # Delete the drive
        db.session.delete(drive)
        db.session.commit()
        cache.delete(f'drive_{drive_id}')
        return jsonify({'message': 'Drive deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
@role_required('company')
def get_drive_applications(drive_id):
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    drive = Drive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({'error': 'Drive not found'}), 404

    applications = Application.query.filter_by(drive_id=drive_id).all()
    return jsonify({
        'applications': [a.to_dict() for a in applications],
        'drive': drive.to_dict(),
    }), 200


@company_bp.route('/applications/<int:application_id>/shortlist', methods=['POST'])
@jwt_required()
@role_required('company')
def shortlist_student(application_id):
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    application = (
        Application.query.join(Drive)
        .filter(Application.id == application_id, Drive.company_id == company.id)
        .first()
    )
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    data = request.get_json() or {}
    application.status = 'Shortlisted'
    if data.get('interview_date'):
        try:
            application.interview_date = datetime.fromisoformat(
                data['interview_date'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
        except ValueError:
            return jsonify({'error': 'Invalid interview_date format'}), 400
    if 'interview_location' in data:
        application.interview_location = data['interview_location']
    if 'remarks' in data:
        application.remarks = data['remarks']

    db.session.commit()
    return jsonify({'message': 'Student shortlisted',
                    'application': application.to_dict()}), 200


@company_bp.route('/applications/<int:application_id>/select', methods=['POST'])
@jwt_required()
@role_required('company')
def select_student(application_id):
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    application = (
        Application.query.join(Drive)
        .filter(Application.id == application_id, Drive.company_id == company.id)
        .first()
    )
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    application.status = 'Selected'
    db.session.commit()
    return jsonify({'message': 'Student selected',
                    'application': application.to_dict()}), 200


@company_bp.route('/applications/<int:application_id>/reject', methods=['POST'])
@jwt_required()
@role_required('company')
def reject_student(application_id):
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    application = (
        Application.query.join(Drive)
        .filter(Application.id == application_id, Drive.company_id == company.id)
        .first()
    )
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    data = request.get_json() or {}
    application.status = 'Rejected'
    if 'remarks' in data:
        application.remarks = data['remarks']

    db.session.commit()
    return jsonify({'message': 'Application rejected',
                    'application': application.to_dict()}), 200


# ---------------------------------------------------------------------------
# Optional: Offer Letter Generator
# ---------------------------------------------------------------------------

@company_bp.route('/applications/<int:application_id>/offer-letter', methods=['GET'])
@jwt_required()
@role_required('company')
def generate_offer_letter(application_id):
    """Generate a dummy HTML offer letter for a Selected student."""
    current_user_id = get_current_user_id()
    company = Company.query.filter_by(user_id=current_user_id).first()
    if not company:
        return jsonify({'error': 'Company profile not found'}), 404

    application = (
        Application.query.join(Drive)
        .filter(Application.id == application_id, Drive.company_id == company.id)
        .first()
    )
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    if application.status != 'Selected':
        return jsonify({'error': 'Offer letter can only be generated for Selected students'}), 400

    student = application.student
    drive = application.drive
    today = datetime.utcnow().strftime('%B %d, %Y')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Offer Letter – {student.full_name}</title>
  <style>
    body {{ font-family: Georgia, serif; max-width: 720px; margin: 60px auto; color: #222; line-height: 1.7; }}
    .header {{ text-align: center; border-bottom: 2px solid #1a237e; padding-bottom: 16px; margin-bottom: 32px; }}
    .header h1 {{ color: #1a237e; margin: 0; }}
    .header p {{ margin: 4px 0; color: #555; }}
    h2 {{ color: #1a237e; }}
    .highlight {{ background: #e8eaf6; padding: 12px 20px; border-radius: 4px; margin: 20px 0; }}
    .signature {{ margin-top: 60px; }}
    .footer {{ margin-top: 60px; font-size: 0.8rem; color: #aaa; text-align: center; border-top: 1px solid #eee; padding-top: 12px; }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{company.company_name}</h1>
    <p>{company.location or ''} | {company.website or ''} | {company.hr_email or ''}</p>
  </div>

  <p>Date: {today}</p>
  <p>Ref: OFFER/{company.id}/{application.id}</p>

  <p>Dear <strong>{student.full_name}</strong>,</p>

  <p>We are delighted to offer you the position of <strong>{drive.job_title}</strong> at
  <strong>{company.company_name}</strong>. After reviewing your profile and performance during
  the selection process, we believe you will be a valuable addition to our team.</p>

  <div class="highlight">
    <h2>Offer Details</h2>
    <table>
      <tr><td><strong>Position:</strong></td><td>{drive.job_title}</td></tr>
      <tr><td><strong>Department:</strong></td><td>{company.industry or 'N/A'}</td></tr>
      <tr><td><strong>Location:</strong></td><td>{drive.location or company.location or 'N/A'}</td></tr>
      <tr><td><strong>CTC:</strong></td><td>{drive.salary_package or 'As per company norms'}</td></tr>
      <tr><td><strong>Roll Number:</strong></td><td>{student.roll_number}</td></tr>
      <tr><td><strong>Branch:</strong></td><td>{student.branch}</td></tr>
    </table>
  </div>

  <p>Please confirm your acceptance of this offer by replying to this letter within
  <strong>7 days</strong> of the date above. This offer is subject to satisfactory completion
  of your degree and verification of all credentials.</p>

  <p>We look forward to welcoming you to {company.company_name}.</p>

  <div class="signature">
    <p>Yours sincerely,</p>
    <br>
    <p><strong>{company.hr_contact or 'HR Department'}</strong><br>
    Human Resources<br>
    {company.company_name}</p>
  </div>

  <div class="footer">
    This is a computer-generated offer letter. — Placement Portal
  </div>
</body>
</html>"""

    # Save to uploads and return as file
    from flask import current_app
    filename = f"offer_letter_{application_id}.html"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write(html)

    return send_file(filepath, as_attachment=True,
                     download_name=f"Offer_Letter_{student.full_name.replace(' ', '_')}.html",
                     mimetype='text/html')
