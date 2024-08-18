from flask import Blueprint, request, jsonify
from models.db_models import db, Accounts, Token, Date
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import generate_csrf, validate_csrf
from decorators.authUdecorator import token_required


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    # Find the user by email
    user = Accounts.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Generate a JWT token
        token = jwt.encode({
            'user_id': user.account_id,
            'exp': datetime.utcnow() + timedelta(hours=7)  # Token expires in 1 hour
        }, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

        # Optionally store the token in the database
        token_record = Token(user_id=user.account_id, token=token, expires_at=datetime.utcnow() + timedelta(hours=1))
        db.session.add(token_record)
        db.session.commit()

        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    # Retrieve form data
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    verified_at_str = request.form.get('verified_at')  # Optional

    # Validate CSRF token
    csrf_token = request.headers.get('X-CSRF-Token')
    if csrf_token:
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            return jsonify({'message': 'Invalid CSRF token'}), 400

    # Validate required fields
    if not email or not username or not password:
        return jsonify({'message': 'Missing required fields'}), 400

    # Handle optional verified_at field
    verified_at = None
    if verified_at_str:
        try:
            verified_at = datetime.fromisoformat(verified_at_str)
        except ValueError:
            return jsonify({'message': 'Invalid date format'}), 400

    # Hash the password before storing
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    # hashed_password = generate_password_hash(password, method='sha256')

    # Create a new date record
    now = datetime.utcnow()
    date_record = Date(created_at=now, updated_at=now)

    try:
        db.session.add(date_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

    # Create a new account with the date record's id
    new_account = Accounts(
        email=email,
        username=username,
        password=hashed_password,
        verified_at=verified_at,
        date_id=date_record.date_id
    )

    try:
        db.session.add(new_account)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/logout', methods=['POST'])
@token_required 
def logout():
    # Get the token from the request
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Missing authorization header'}), 401

    token = auth_header.split(' ')[1]  # Assuming the format is "Bearer <token>"

    # Remove the token from the database
    try:
        token_record = Token.query.filter_by(token=token).first()
        if token_record:
            db.session.delete(token_record)
            db.session.commit()
            return jsonify({'message': 'Logged out successfully'}), 200
        else:
            return jsonify({'message': 'Invalid token'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@auth_bp.route('/csrf-token', methods=['GET'])
def csrf_token():
    # Return the CSRF token
    token = generate_csrf()
    return jsonify({'csrfToken': token}), 200


