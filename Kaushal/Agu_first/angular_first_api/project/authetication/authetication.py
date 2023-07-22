from flask import Blueprint,request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token
import os


authetication_bp = Blueprint('auth', __name__)



@authetication_bp.post('/register')
def register():
    try:
        role = request.json.get('role')
        firstname = request.json.get('firstname')
        lastname = request.json.get('lastname')
        email = request.json.get('email')
        gender = request.json.get('gender')
        password = request.json.get('password')

        if role not in ['admin', 'normal']:
            return jsonify({"message": "role must be 'admin' or 'normal'"}), 400

        if not firstname:
            return jsonify({'error': 'firstname is required'}), 400

        if not lastname:
            return jsonify({'error': 'lastname is required'}), 400

        if not email:
            return jsonify({'error': 'email is required'}), 400

        if gender not in ['male', 'female']:
            return jsonify({"message": "gender must be 'male' or 'female'"}), 400

        if not password:
            return jsonify({'error': 'password is required'}), 400

        cursor = g.db.cursor()

        password = generate_password_hash(password, method='sha256', salt_length=8)
        cursor.execute(
            'INSERT INTO tbl_users (role, firstname, lastname, email, gender, password) VALUES (%s, %s, %s, %s, %s, %s)',
            (role, firstname, lastname, email, gender, password))
        g.db.commit()

        return jsonify({'message': 'User registered'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@authetication_bp.post('/login')
def login():
    try:
        
        email = request.json.get('email')
        password = request.json.get('password')
        
        if not email:
            return jsonify({'error': 'Email field is required'}), 400
        
        if not password:
            return jsonify({'error': 'Password field is required'}), 400
        
        cursor = g.db.cursor()
        cursor.execute(f"SELECT * FROM tbl_users WHERE email='{email}' AND is_active=1 AND is_delete=0")
        user = cursor.fetchone()

        if user:
            is_pass_correct = check_password_hash(user[6], password)
            if is_pass_correct:
                access = create_access_token(identity=user[0])
                return jsonify({
                    'user': {
                        'access': access,
                        'Empolyee Name': user[2]
                    }
                }), 200
        
        return jsonify({'message' : 'Invalid email or password'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
