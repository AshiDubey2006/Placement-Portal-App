from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db, cache
from app.models.user import User
from app.models.company import Company
from app.models.student import Student
from app.models.drive import Drive
from app.models.application import Application
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_dashboard():
    """Get admin dashboard statistics"""
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = Drive.query.count()
    total_applications = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status='Pending').count()
    pending_drives = Drive.query.filter_by(status='Pending').count()
    
    return jsonify({
        'total_students': total_students,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'pending_companies': pending_companies,
        'pending_drives': pending_drives
    }), 200

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_companies():
    """Get all companies with optional search"""
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Company.query.join(User)
    
    if search:
        query = query.filter(Company.company_name.ilike(f'%{search}%'))
    
    if status:
        query = query.filter(Company.approval_status == status)
    
    companies = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'companies': [c.to_dict() for c in companies.items],
        'total': companies.total,
        'pages': companies.pages,
        'current_page': page
    }), 200

@admin_bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@jwt_required()
@role_required('admin')
def approve_company(company_id):
    """Approve a company registration"""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Approved'
    db.session.commit()
    
    # Clear cache
    cache.delete(f'company_{company_id}')
    
    return jsonify({'message': 'Company approved successfully', 'company': company.to_dict()}), 200

@admin_bp.route('/companies/<int:company_id>/reject', methods=['POST'])
@jwt_required()
@role_required('admin')
def reject_company(company_id):
    """Reject a company registration"""
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'Rejected'
    db.session.commit()
    
    # Clear cache
    cache.delete(f'company_{company_id}')
    
    return jsonify({'message': 'Company rejected successfully', 'company': company.to_dict()}), 200

@admin_bp.route('/companies/<int:company_id>/blacklist', methods=['POST'])
@jwt_required()
@role_required('admin')
def blacklist_company(company_id):
    """Blacklist a company"""
    company = Company.query.get_or_404(company_id)
    company.user.is_blacklisted = True
    db.session.commit()
    
    return jsonify({'message': 'Company blacklisted successfully'}), 200

@admin_bp.route('/companies/<int:company_id>/activate', methods=['POST'])
@jwt_required()
@role_required('admin')
def activate_company(company_id):
    """Activate a blacklisted company"""
    company = Company.query.get_or_404(company_id)
    company.user.is_blacklisted = False
    db.session.commit()
    
    return jsonify({'message': 'Company activated successfully'}), 200

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_students():
    """Get all students with optional search"""
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Student.query.join(User)
    
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) |
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.roll_number.ilike(f'%{search}%'))
        )
    
    students = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'students': [s.to_dict() for s in students.items],
        'total': students.total,
        'pages': students.pages,
        'current_page': page
    }), 200

@admin_bp.route('/students/<int:student_id>/blacklist', methods=['POST'])
@jwt_required()
@role_required('admin')
def blacklist_student(student_id):
    """Blacklist a student"""
    student = Student.query.get_or_404(student_id)
    student.user.is_blacklisted = True
    db.session.commit()
    
    return jsonify({'message': 'Student blacklisted successfully'}), 200

@admin_bp.route('/students/<int:student_id>/activate', methods=['POST'])
@jwt_required()
@role_required('admin')
def activate_student(student_id):
    """Activate a blacklisted student"""
    student = Student.query.get_or_404(student_id)
    student.user.is_blacklisted = False
    db.session.commit()
    
    return jsonify({'message': 'Student activated successfully'}), 200

@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_drives():
    """Get all drives with optional search"""
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Drive.query.join(Company)
    
    if search:
        query = query.filter(Drive.job_title.ilike(f'%{search}%'))
    
    if status:
        query = query.filter(Drive.status == status)
    
    drives = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'drives': [d.to_dict() for d in drives.items],
        'total': drives.total,
        'pages': drives.pages,
        'current_page': page
    }), 200

@admin_bp.route('/drives/<int:drive_id>/approve', methods=['POST'])
@jwt_required()
@role_required('admin')
def approve_drive(drive_id):
    """Approve a placement drive"""
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Approved'
    db.session.commit()
    
    # Clear cache
    cache.delete(f'drive_{drive_id}')
    
    return jsonify({'message': 'Drive approved successfully', 'drive': drive.to_dict()}), 200

@admin_bp.route('/drives/<int:drive_id>/reject', methods=['POST'])
@jwt_required()
@role_required('admin')
def reject_drive(drive_id):
    """Reject a placement drive"""
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Closed'
    db.session.commit()
    
    # Clear cache
    cache.delete(f'drive_{drive_id}')
    
    return jsonify({'message': 'Drive rejected successfully', 'drive': drive.to_dict()}), 200

@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_all_applications():
    """Get all applications"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    applications = Application.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'applications': [a.to_dict() for a in applications.items],
        'total': applications.total,
        'pages': applications.pages,
        'current_page': page
    }), 200

@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_statistics():
    """Get placement statistics"""
    total_drives = Drive.query.count()
    approved_drives = Drive.query.filter_by(status='Approved').count()
    total_applications = Application.query.count()
    selected_students = Application.query.filter_by(status='Selected').count()
    shortlisted_students = Application.query.filter_by(status='Shortlisted').count()
    
    # Get statistics by branch
    branch_stats = db.session.query(
        Student.branch,
        db.func.count(Student.id).label('count')
    ).group_by(Student.branch).all()
    
    # Get statistics by company
    company_stats = db.session.query(
        Company.company_name,
        db.func.count(Drive.id).label('drive_count'),
        db.func.count(Application.id).label('application_count')
    ).join(Drive, Company.id == Drive.company_id)\
     .outerjoin(Application, Drive.id == Application.drive_id)\
     .group_by(Company.id).all()
    
    return jsonify({
        'total_drives': total_drives,
        'approved_drives': approved_drives,
        'total_applications': total_applications,
        'selected_students': selected_students,
        'shortlisted_students': shortlisted_students,
        'branch_stats': [{'branch': b[0], 'count': b[1]} for b in branch_stats],
        'company_stats': [{'company': c[0], 'drives': c[1], 'applications': c[2]} for c in company_stats]
    }), 200
