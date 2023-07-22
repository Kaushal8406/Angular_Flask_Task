from flask import Blueprint,request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from random import randint
from flask_mail import Mail, Message
import random
import string



authetication_bp = Blueprint('auth', __name__)


blacklist = set()
print(blacklist)



def generate_token(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_otp():
    otp = random.randint(1000, 9999)
    return str(otp)


# New user registration
@authetication_bp.post('/register')
def register():
    try:
        data = request.json
        role = data.get('role')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        email = data.get('email')
        password = data.get('password')

        if role not in ['admin', 'user']:
            return jsonify({"message": "Role must be 'admin' or 'user'"}), 400

        if not firstname:
            return jsonify({'error': 'First Name is required'}), 400

        if not lastname:
            return jsonify({'error': 'Last Name is required'}), 400

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        password_hash = generate_password_hash(password)

        token = generate_token()

        cursor = g.db.cursor()
        cursor.execute('INSERT INTO tbl_user (role, firstname, lastname, email, password, token) VALUES (%s, %s, %s, %s, %s, %s)',
                       (role, firstname, lastname, email, password_hash, token))
        g.db.commit()

        cursor.execute('SELECT id FROM tbl_user WHERE is_active=1 AND is_delete=0 AND email=%s', (email,))
        user = cursor.fetchone()
        
        if user is None:
            return jsonify({'error': 'Failed to retrieve user information'}), 500

        user_id = user[0]

        otp = generate_otp()

        cursor.execute('INSERT INTO tbl_user_otp (user_id, verification_token, otp) VALUES (%s, %s, %s)',
                       (user_id, token, otp))
        g.db.commit()

        msg = Message(
            'OTP',
            sender='jigoprajapati01@gmail.com',
            recipients=[email]
        )

        link = 'http://localhost:4200/registration_otp'

        msg.body = f'Your OTP: {otp}\nUser Token: {token}\n URL: {link}'
       
        from project import mail
        mail.send(msg)

        return jsonify({'message': 'User registered', 'user_id': user_id}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@authetication_bp.post('/otp')
def otp():
    try:
        otp = request.json.get('otp')
        token = request.json.get('token')

        if not otp:
            return jsonify({"error": "OTP is required"}), 400

        if not token:
            return jsonify({"error": "Token is required"}), 400

        cursor = g.db.cursor()
        cursor.execute(
            f"SELECT o.user_id, o.verification_token, o.otp FROM tbl_user_otp o JOIN tbl_user tu ON o.user_id = tu.id WHERE o.verification_token = '{token}'"
        )
       

        result = cursor.fetchone()

        if not result:
            return jsonify({'error': "Invalid token"}), 400

        stored_user_id, stored_verification_token, stored_otp = result

        if int(otp) != stored_otp:
            return jsonify({'error': "OTP does not match"}), 400

        verify = 1
       
        cursor.execute('UPDATE tbl_user SET is_verify=%s WHERE id=%s', (verify, stored_user_id))
        g.db.commit()

        return jsonify({'message': 'OTP successfully matched'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@authetication_bp.post('/login')
def login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        if not email:
            return jsonify({'error': 'Email is required'}), 400
       
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM tbl_user WHERE email = %s AND is_active = 1 AND is_delete = 0 AND is_verify = 1", (email,))
        
        user = cursor.fetchone()

        if user is None:
            return jsonify({'message': 'User Not Found'}), 404

        user_id = user[0]
        user_role = user[1]
        verify = user[6]

        if verify != 1:
            return jsonify({'error': 'User is not verified'}), 403
        
        otp = generate_otp()
        is_pass_correct = check_password_hash(user[5], password)

        if user_role == 'user' and is_pass_correct:
            
            cursor.execute('INSERT INTO tbl_user_login_otp (user_id, otp) VALUES (%s, %s)', (user_id, otp))
            g.db.commit()

            msg = Message(
                'OTP',
                sender='jigoprajapati01@gmail.com',
                recipients=[email]
            )
            msg.body = f'Your OTP: {otp}'

            from project import mail
            mail.send(msg)

            return jsonify({
                    'user': {
                        'message': 'Message send The Email',
                        'name': user[2],
                        'user_type': user[1]
                    }
                }), 200
        
        else:
            is_pass_correct = check_password_hash(user[5], password)
            if is_pass_correct:
                access = create_access_token(identity=user[0])
                return jsonify({
                    'user': {
                        'access': access,
                        'name': user[2],
                        'user_type': user[1]
                    }
                }), 200
            else:
                return jsonify({'message' : 'Password are Incorrect'}), 403

    except Exception as e:
        return jsonify({'error': str(e)}), 500







@authetication_bp.post('/user_login_otp')
def user_login_otp():
    try:
        otp = request.json.get('otp')

        if not otp:
            return jsonify({"error": "OTP is required"}), 400

        cursor = g.db.cursor()
        
        cursor.execute(
            'SELECT tu.id, tu.firstname, o.otp FROM tbl_user_login_otp o JOIN tbl_user tu ON o.user_id = tu.id WHERE o.otp = %s',
            (otp,))
        user = cursor.fetchone()
        
        if user is None:
            return jsonify({'message': "OTP not Metch found"}), 404

        stored_otp = user[2]

        if int(otp) == stored_otp:
            access = create_access_token(identity=user[0])
            
            cursor.execute(f'DELETE FROM tbl_user_login_otp WHERE otp = {otp}')
            g.db.commit()
            
            return jsonify({
                'user': {
                    'access': access,
                    'name': user[1]
                }
            }), 200
        
        else:
            return jsonify({'error': "OTP does not match"}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


