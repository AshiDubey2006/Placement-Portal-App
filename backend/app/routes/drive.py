from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db, cache
from app.models.user import User
from app.models.student import Student
from app.models.drive import Drive
from app.models.company import Company
from app.models.application import Application
from app.utils.decorators import role_required, get_current_user_id
from datetime import datetime

drive_bp = Blueprint('drive', __name__)


@drive_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_drives():
    """Get all approved drives with optional search and filters."""
    search = request.args.get('search', '')
    branch = request.args.get('branch', '')
    min_cgpa = request.args.get('min_cgpa', 0, type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Drive.query.filter_by(status='Approved').join(Company)

    if search:
        query = query.filter(
            Drive.job_title.ilike(f'%{search}%') |
            Company.company_name.ilike(f'%{search}%')
        )

    drives_paginated = query.order_by(Drive.application_deadline.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)

    if user and user.role == 'student':
        student = Student.query.filter_by(user_id=current_user_id).first()
        if student:
            filtered_drives = []
            for drive in drives_paginated.items:
                drive_dict = drive.to_dict()
                drive_dict['is_eligible'] = drive.is_eligible(student)
                already_applied = Application.query.filter_by(
                    student_id=student.id,
                    drive_id=drive.id
                ).first()
                drive_dict['already_applied'] = bool(already_applied)
                filtered_drives.append(drive_dict)

            return jsonify({
                'drives': filtered_drives,
                'total': drives_paginated.total,
                'pages': drives_paginated.pages,
                'current_page': page
            }), 200

    return jsonify({
        'drives': [d.to_dict() for d in drives_paginated.items],
        'total': drives_paginated.total,
        'pages': drives_paginated.pages,
        'current_page': page
    }), 200


@drive_bp.route('/<int:drive_id>', methods=['GET'])
@jwt_required()
def get_drive_details(drive_id):
    """Get drive details."""
    drive = Drive.query.get_or_404(drive_id)
    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)

    drive_dict = drive.to_dict()

    if user and user.role == 'student':
        student = Student.query.filter_by(user_id=current_user_id).first()
        if student:
            drive_dict['is_eligible'] = drive.is_eligible(student)
            already_applied = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first()
            drive_dict['already_applied'] = bool(already_applied)

    return jsonify(drive_dict), 200


@drive_bp.route('/<int:drive_id>/apply', methods=['POST'])
@jwt_required()
@role_required('student')
def apply_for_drive(drive_id):
    """Apply for a placement drive."""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()

    if not student:
        return jsonify({'error': 'Student profile not found'}), 404

    drive = Drive.query.get_or_404(drive_id)

    if drive.status != 'Approved':
        return jsonify({'error': 'Drive is not open for applications'}), 400

    if drive.application_deadline and drive.application_deadline < datetime.utcnow():
        return jsonify({'error': 'Application deadline has passed'}), 400

    if not drive.is_eligible(student):
        return jsonify({'error': 'You are not eligible for this drive'}), 400

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing_application:
        return jsonify({'error': 'You have already applied for this drive'}), 400

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status='Applied'
    )

    try:
        db.session.add(application)
        db.session.commit()
        # Invalidate cached drives list
        cache.clear()
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@drive_bp.route('/search', methods=['GET'])
@jwt_required()
def search_drives():
    """Search drives with various filters."""
    search = request.args.get('search', '')
    company = request.args.get('company', '')
    location = request.args.get('location', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Drive.query.filter_by(status='Approved').join(Company)

    if search:
        query = query.filter(
            Drive.job_title.ilike(f'%{search}%') |
            Drive.job_description.ilike(f'%{search}%') |
            Company.company_name.ilike(f'%{search}%')
        )

    if company:
        query = query.filter(Company.company_name.ilike(f'%{company}%'))

    if location:
        query = query.filter(Drive.location.ilike(f'%{location}%'))

    drives_paginated = query.order_by(Drive.application_deadline.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    current_user_id = get_current_user_id()
    user = User.query.get(current_user_id)

    drives_list = []
    for drive in drives_paginated.items:
        drive_dict = drive.to_dict()
        if user and user.role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if student:
                drive_dict['is_eligible'] = drive.is_eligible(student)
                already_applied = Application.query.filter_by(
                    student_id=student.id,
                    drive_id=drive.id
                ).first()
                drive_dict['already_applied'] = bool(already_applied)
        drives_list.append(drive_dict)

    return jsonify({
        'drives': drives_list,
        'total': drives_paginated.total,
        'pages': drives_paginated.pages,
        'current_page': page
    }), 200
