from flask import Blueprint,request, jsonify, g, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
import os
from mysql.connector import IntegrityError
import random
import re

authetication_bp = Blueprint('auth', __name__)


def generate_otp():
    id = random.randint(1000, 9999)
    return str(id)


@authetication_bp.post('/register')
def register():
    try:
        email = request.json.get('email')

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if re.match(email_regex, email):
            pass
        else:
             return jsonify({'error': 'invalid Email'}),400

    
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        cursor = g.db.cursor()

        cursor.execute("SELECT email FROM tbl_user WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            return jsonify({'error': "User Already Exist With This Email"}), 404
        
        cursor.execute(f"DELETE FROM tbl_temporary_user WHERE email = '{email}'")
        g.db.commit()

        cursor.execute(
            'INSERT INTO tbl_temporary_user (email) VALUES (%s)',
            (email,))
        g.db.commit()

        cursor.execute(
            'SELECT id, email FROM tbl_temporary_user WHERE is_active=1 AND is_delete=0 AND email=%s ORDER BY id DESC LIMIT 1',
            (email,))
        
        users = cursor.fetchall()

        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        for user in users:
            user_id = user[0]
            email = user[1]

        otp = generate_otp()
        
        cursor.execute(
            'INSERT INTO tbl_otp (user_id, otp) VALUES (%s, %s)',
            (user_id, otp,))
        g.db.commit()

        msg = Message(
            'User Profile',
            sender=email,
            recipients=[email]
        )
        
        msg.html = f"""<h2>Verification Code</h2>
                    <p>Please use the Verification Code below to Sign In.</p>
                    <h6>User Email: {email} </h6>
                    <h4>{otp}</h4>
                    <p>If You didn't request this, you can ingore this email.</p>
                    <p>Thanks,<br>
                    Kaushal Prajapati</p>"""
        
        msg.subject = 'Verification Code'

        from project import mail
        mail.send(msg)
        return jsonify({'message': 'User registered'}), 201

    except IntegrityError:
        return jsonify({"error": "User Already Exist With This Email"}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 404







@authetication_bp.post('/otp')
def user_login_otp():
    try:
        coine = 5000
        otp = request.json.get('otp')

        if not otp:
            return jsonify({"error": "OTP is required"}), 400
        
        if not otp.isdigit():
            return jsonify({'error': 'Please Enter Only Numeric Digits'}), 400

        otp_len = len(otp)

        if otp_len < 4 or otp_len > 4:
            return jsonify({"error": 'Only Four Digit Enter'}),400
       
      
        referral_code = request.json.get('referral_code')

        cursor = g.db.cursor()
        cursor.execute(
            'SELECT tu.id,o.otp,tu.email FROM tbl_otp o JOIN tbl_temporary_user tu ON o.user_id = tu.id WHERE o.otp = %s ORDER BY user_id DESC LIMIT 1',
            (otp,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'error': "OTP Does Not match"}), 404

        user_id = user[0]
        stored_otp = user[1]
        email = user[2]

        if int(otp) == stored_otp:
            verify = 1

            if not referral_code:
                cursor.execute('INSERT INTO tbl_user (email,coine,is_verify) VALUES (%s,%s,%s)',(email,coine,verify))
                cursor.execute(f'DELETE FROM tbl_otp WHERE otp = {otp}')
                g.db.commit()
                return jsonify({"message": "Successfully matched OTP"}), 200
            else: 
                is_valid = 1
                coine = coine + 1000
                cursor.execute('INSERT INTO tbl_referral_code (user_id,referral_code,is_valid) VALUES (%s, %s, %s)',(user_id, referral_code,is_valid))
                
                cursor.execute('INSERT INTO tbl_user (email,coine,is_verify) VALUES (%s,%s,%s)',(email,coine,verify))
                
                cursor.execute(f'DELETE FROM tbl_otp WHERE otp = {otp}')
                g.db.commit()
                return jsonify({"message": "Successfully matched OTP and updated coins"}), 200

        else:
            return jsonify({'error': "OTP does not match"}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400




@authetication_bp.post('/login')
def login():
    try:
        email = request.json.get('email')
       
        if not email:
            return jsonify({'error': 'Email field is required'}), 400
        
        cursor = g.db.cursor()
        cursor.execute(f"SELECT * FROM tbl_user WHERE email='{email}' AND is_verify = 1 AND is_active=1 AND is_delete=0")
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Email Is Not Found'}),404
      
        id  = user[0]
     
        
        msg = Message(
            'User Profile',
            sender=email,
            recipients=[email]
        )

       
        otp = generate_otp()

        cursor.execute(f"DELETE FROM tbl_login_otp WHERE user_id = '{id}'")
        g.db.commit()

        cursor.execute(
            'INSERT INTO tbl_login_otp (user_id, otp) VALUES (%s, %s)',
            (id, otp))
        g.db.commit()

        msg.body = f"""Please use the Verification Code below to Login In.\n\n{otp}\n\n If You didn't request this, you can ingore this email."""
        
        msg.subject = 'Login Varifaction Code'
        from project import mail
        mail.send(msg)
        

        if user:
                access = create_access_token(identity=user[0])
                return jsonify({
                    'user': {
                        'access': access,
                        'User Email': user[1]
                    }
                }), 200
        return jsonify({'message' : 'Invalid email'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 404

   



@authetication_bp.post('/Verfication_login_otp')  
@jwt_required() 
def Verfication_login_otp():
    try:
    
        id = get_jwt_identity()
        login_otp = request.json.get('login_otp')

        if not login_otp:
            return jsonify({"error": "OTP is required"}), 400

        cursor = g.db.cursor()
        cursor.execute(
            'SELECT otp FROM tbl_login_otp WHERE user_id=%s AND otp=%s',
            (id, login_otp))
        
        user = cursor.fetchone()
    
        if user is None:
            return jsonify({'error': "OTP does not match"}), 404
        
        cursor.execute(f'DELETE FROM tbl_login_otp WHERE otp = {login_otp}')
                
        g.db.commit()
        
        return jsonify({"message": "Successfully matched OTP"}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 404


