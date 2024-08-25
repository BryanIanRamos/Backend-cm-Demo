from functools import wraps
from flask import request, jsonify
import jwt
from models.db_models import Token
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401
        
        token = auth_header.split(' ')[1]  # Assuming the format is "Bearer <token>"
        
        try:
            decoded_token = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            # Optionally verify the token in the database
            token_record = Token.query.filter_by(token=token).first()
            if not token_record:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
# jjk
    return decorated_function
