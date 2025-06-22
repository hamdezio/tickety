from flask import Blueprint, request, jsonify, current_app, g
from models import User
from mongoengine.errors import NotUniqueError
import bcrypt
import jwt
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # JWT token sent in Authorization header "Bearer <token>"
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]

        if not token:
            return jsonify({'error': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = User.objects(username=data['username']).first()
            if not user:
                return jsonify({'error': 'User not found!'}), 401
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired! Please log in again.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Default role is 'client'; admins must be added manually
    role = 'client'

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        user = User(username=username, password=hashed_password.decode('utf-8'), role=role)
        user.save()
    except NotUniqueError:
        return jsonify({'error': 'Username already exists'}), 409

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.objects(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate JWT token
    token = jwt.encode(
        {'username': user.username},
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({'token': token}), 200
