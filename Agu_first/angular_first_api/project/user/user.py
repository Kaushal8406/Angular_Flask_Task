from flask import Blueprint,request, jsonify, g
from flask_jwt import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename


user_bp = Blueprint('user', __name__)


@user_bp.post('/contact_us')
def contact_us():
    try:  
        fullname = request.json.get('fullname')
        email = request.json.get('email')
        phone_number = request.json.get('phone_number')
        message = request.json.get('message')

        if not fullname:
            return jsonify({'error': 'fullname is required'}), 400

        if not email:
            return jsonify({'error': 'email is required'}), 400
        
        if not phone_number:
            return jsonify({'error': 'phone_number is required'}), 400

        cursor = g.db.cursor()

        cursor.execute(
            'INSERT INTO tbl_contact_us (fullname, email,phone_number, message) VALUES (%s, %s, %s, %s)',
            (fullname, email, phone_number, message))
        g.db.commit()

        return jsonify({'message': 'Successfully Inserted'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@user_bp.post('/about_us')
# @jwt_required()
def about_us():
    try:
        avatar = request.files['image']

        if not avatar:
            return jsonify({'error': 'No Image selected'}), 400
        
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join('project/media', filename))

        titel = request.form.get('titel')

        if not titel:
            return jsonify({'error': 'Titel is required'}), 400
        

        description = request.form.get('description')

        if not description:
            return jsonify({'error': 'description is required'}), 400
        

        cursor = g.db.cursor()
        cursor.execute(
            'INSERT INTO tbl_about (img, titel, description) VALUES (%s, %s, %s)',
            (filename, titel, description))
        g.db.commit()

        return jsonify({'message': 'Successfully Inserted'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@user_bp.get('/about_us_list')
# @jwt_required()
def about_us_list():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT id, img,titel,description FROM tbl_about')
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

























@user_bp.get('/newsletter_list')
# @jwt_required()
def newsletter_list():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT id,image,titel,description FROM tbl_newsletter')
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@user_bp.get('/product_list')
# @jwt_required()
def product_list():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT id,product_img,product_title,product_description FROM tbl_product')
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@user_bp.get('/services_list')
# @jwt_required()
def services_list():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT id,services FROM tbl_services')
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500