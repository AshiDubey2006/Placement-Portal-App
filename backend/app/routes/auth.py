from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from app import db
from app.models.user import User
from app.models.company import Company
from app.models.student import Student
from app.utils.decorators import get_current_user_id

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('role'):
        return jsonify({'error': 'Missing required fields'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    if data['role'] not in ['company', 'student']:
        return jsonify({'error': 'Invalid role. Must be company or student.'}), 400

    user = User(email=data['email'], role=data['role'])
    user.set_password(data['password'])
    try:
        db.session.add(user)
        db.session.commit()
        if data['role'] == 'company':
            db.session.add(Company(
                user_id=user.id,
                company_name=data.get('company_name', ''),
                hr_contact=data.get('hr_contact', ''),
                hr_email=data.get('hr_email', data['email']),
                website=data.get('website', ''),
                description=data.get('description', ''),
                industry=data.get('industry', ''),
                location=data.get('location', '')
            ))
        elif data['role'] == 'student':
            db.session.add(Student(
                user_id=user.id,
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                roll_number=data.get('roll_number', ''),
                branch=data.get('branch', ''),
                year=data.get('year', 1),
                cgpa=data.get('cgpa', 0.0),
                phone=data.get('phone', '')
            ))
        db.session.commit()
        return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    if user.is_blacklisted:
        return jsonify({'error': 'Account is blacklisted'}), 403

    # identity MUST be a string in Flask-JWT-Extended >= 4.x
    access_token = create_access_token(identity=str(user.id))

    response_data = user.to_dict()
    if user.role == 'company' and user.company:
        response_data['company'] = user.company.to_dict()
    elif user.role == 'student' and user.student:
        response_data['student'] = user.student.to_dict()

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': response_data
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user = User.query.get(get_current_user_id())
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = user.to_dict()
    if user.role == 'company' and user.company:
        data['company'] = user.company.to_dict()
    elif user.role == 'student' and user.student:
        data['student'] = user.student.to_dict()
    return jsonify(data), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400
    user = User.query.get(get_current_user_id())
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'}), 200
