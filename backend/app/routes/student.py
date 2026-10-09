from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from app import db, cache
from app.models.user import User
from app.models.student import Student
from app.models.drive import Drive
from app.models.application import Application
from app.utils.decorators import role_required, get_current_user_id
from app.utils.file_helpers import save_file
from app.tasks.export_tasks import export_applications_csv
import os
from datetime import datetime

student_bp = Blueprint('student', __name__)

@student_bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required('student')
def get_student_profile():
    """Get student profile"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    return jsonify(student.to_dict()), 200

@student_bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required('student')
def update_student_profile():
    """Update student profile"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'phone' in data:
        student.phone = data['phone']
    if 'skills' in data:
        student.skills = data['skills']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully', 'student': student.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/resume', methods=['POST'])
@jwt_required()
@role_required('student')
def upload_resume():
    """Upload student resume"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['resume']
    from flask import current_app
    filename = save_file(file, current_app.config['UPLOAD_FOLDER'], current_app.config['ALLOWED_EXTENSIONS'])
    
    if not filename:
        return jsonify({'error': 'Invalid file format'}), 400
    
    # Delete old resume if exists
    if student.resume_path:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], student.resume_path)
        if os.path.exists(old_path):
            os.remove(old_path)
    
    student.resume_path = filename
    db.session.commit()
    
    return jsonify({'message': 'Resume uploaded successfully', 'resume_path': filename}), 200

@student_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('student')
def student_dashboard():
    """Get student dashboard"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get approved drives
    approved_drives = Drive.query.filter_by(status='Approved').all()
    
    # Filter eligible drives
    eligible_drives = []
    for drive in approved_drives:
        if drive.is_eligible(student):
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first()
            drive_dict = drive.to_dict()
            drive_dict['already_applied'] = bool(already_applied)
            eligible_drives.append(drive_dict)
    
    # Get student's applications
    applications = Application.query.filter_by(student_id=student.id).all()
    
    return jsonify({
        'student': student.to_dict(),
        'eligible_drives': eligible_drives,
        'my_applications': [a.to_dict() for a in applications],
        'total_applications': len(applications)
    }), 200

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
@role_required('student')
def get_student_applications():
    """Get student's application history"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    applications = Application.query.filter_by(student_id=student.id).all()
    
    return jsonify({
        'applications': [a.to_dict() for a in applications]
    }), 200

@student_bp.route('/applications/export', methods=['POST'])
@jwt_required()
@role_required('student')
def export_applications():
    """Trigger CSV export of student's applications (async job)"""
    current_user_id = get_current_user_id()
    student = Student.query.filter_by(user_id=current_user_id).first()
    
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Trigger async job
    task = export_applications_csv.delay(student.id)
    
    return jsonify({
        'message': 'Export job started',
        'task_id': task.id
    }), 202

@student_bp.route('/applications/export/status/<task_id>', methods=['GET'])
@jwt_required()
@role_required('student')
def get_export_status(task_id):
    """Get export job status"""
    from app.tasks.export_tasks import celery_app
    from celery.result import AsyncResult
    
    result = AsyncResult(task_id, app=celery_app)
    
    if result.ready():
        if result.successful():
            return jsonify({
                'status': 'completed',
                'file_path': result.result
            }), 200
        else:
            return jsonify({
                'status': 'failed',
                'error': str(result.result)
            }), 500
    else:
        return jsonify({
            'status': 'pending'
        }), 200

@student_bp.route('/applications/download/<filename>', methods=['GET'])
@jwt_required()
@role_required('student')
def download_export(filename):
    """Download exported CSV file"""
    from flask import current_app
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)
