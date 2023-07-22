from flask import Blueprint,request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from random import randint
from flask_mail import Mail, Message
import random
import string
from mysql.connector import IntegrityError


authetication_bp = Blueprint('auth', __name__)


blacklist = set()
print(blacklist)

import string
import random

def generate_token(length=6):
    chars = string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_id():
    id = random.randint(100, 999)
    return str(id)

# New user registration
@authetication_bp.post('/register')
def register():
    try:
        data = request.json
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
       
        if not username and username == '':
            return jsonify({'error': 'UserName is required'}), 400

        if not name and name == '':
            return jsonify({'error': 'Last Name is required'}), 400

        if not email and email == '':
            return jsonify({'error': 'Email is required'}), 400

        REGID  = generate_id()

        cursor = g.db.cursor()
        cursor.execute('INSERT INTO tbl_user (Regid, username, name, email) VALUES (%s, %s, %s, %s)',
                       (REGID, username, name, email))
        g.db.commit()
    
        msg = Message(
            'User Profile',
            sender='email',
            recipients=['kaushalprajapati@hyperlinkinfosystem.net.in']
        )
       
        msg.body = f'REGID: {REGID}\n Your Username: {username}\n User Email: {email}\n'
       
        from project import mail
        mail.send(msg)

        return jsonify({'message': 'User registered'}), 201
    
    except KeyError:
        return jsonify({"massage":"no data found"}),404

    except IntegrityError:
        return jsonify({"massage":"User Already Exist With This Email"}),400

    except Exception as e:
        return jsonify({'error': str(e)}), 404




#login---------------
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
        cursor.execute("SELECT * FROM tbl_user WHERE email = %s AND role = 'user' AND is_active = 1 AND is_delete = 0", (email,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'error': 'User Not Found'}), 404

        verify = user[7]
  
        is_pass_correct = check_password_hash(user[6], password)

        if is_pass_correct and verify == 0:
            access = create_access_token(identity=user[0])
        
            return jsonify({
                    'user': {
                        'access': access,
                        'name': user[3],
                        'Message': 'Pending'
                    }
                }), 200
        
        else: 
            is_pass_correct = check_password_hash(user[6], password)
            if is_pass_correct:
                access = create_access_token(identity=user[0])
                return jsonify({
                    'user': {
                        'access': access,
                        'name': user[3],
                        'Message': 'Complete'
                    }
                }), 200
            else:
                return jsonify({'error' : 'Password are Incorrect'}), 403

    except Exception as e:
        return jsonify({'error': str(e)}), 404



@authetication_bp.post('/change_password')
@jwt_required()
def change_password():
    try:
        id =  get_jwt_identity()
        password = request.json.get('password')

        if not password:
            return jsonify({"error": "password is required"}), 400
        
        cursor = g.db.cursor()
        verify = 1
        password_hash = generate_password_hash(password)

        cursor.execute('UPDATE tbl_user SET is_verify = %s, password= %s WHERE id = %s', (verify, password_hash, id))
        g.db.commit()



        return jsonify({'message': 'Successfully Password Change'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 404






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
        return jsonify({'error': str(e)}), 404


@authetication_bp.post('/admin_password/<id>')
def admin_password(id):
    try:

            token = generate_token()

            password_hash = generate_password_hash(token)

            cursor = g.db.cursor()

            cursor.execute('UPDATE tbl_user SET password= %s WHERE Regid = %s', (password_hash, id))

            g.db.commit()

            msg = Message(
                    'Temporary Password',
                    sender='jigoprajapati01@gmail.com',
                    recipients=['kaushalprajapati589412@gmail.com']
                )
            
            msg.body = f'Temporary Password: {token}\n Regid: {id} '
            
            from project import mail
            mail.send(msg)
            return jsonify({'Message': 'Send Temporary Password'}),201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 404



#Admin Login---------------
@authetication_bp.post('/admin_login')
def admin_login():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        if not email:
            return jsonify({'error': 'Email is required'}), 400
       
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        cursor = g.db.cursor()
        cursor.execute("SELECT * FROM tbl_user WHERE email = %s AND role = 'admin' AND is_active = 1 AND is_delete = 0", (email,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'error': 'Admin Not Found'}), 404

    
        is_pass_correct = check_password_hash(user[6], password)

        if is_pass_correct:
            access = create_access_token(identity=user[0])
        
            return jsonify({
                    'user': {
                        'access': access,
                        'name': user[3]
                    }
                }), 200
        

    except Exception as e:
        return jsonify({'error': str(e)}), 404
