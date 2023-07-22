from flask import Blueprint, request, jsonify,g
from flask_jwt import jwt_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

def is_admin(user_id):
    cur = g.db.cursor()
    cur.execute(f"select role from tbl_users where id={user_id}")
    user = cur.fetchone()
    if user:
        if user[0] == 'admin':
            return True
        return False

admin_bp = Blueprint('admin', __name__)
  

@admin_bp.delete('/delete_employee')
@jwt_required()
def delete_employee():
    try:
        user_id = get_jwt_identity()

        if not is_admin(user_id):
            return jsonify({"error": "Unauthorized Access"}), 401


        employee_id = request.json.get('user_id')

        cursor = g.db.cursor()

        cursor.execute(f'SELECT id FROM tbl_users WHERE id = {employee_id} AND role="normal" ')
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Employee not found'}), 404
       
        cursor.execute(f'DELETE FROM tbl_users WHERE id = {employee_id}')
        g.db.commit()

        return jsonify({'message': 'Employee successfully deleted'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@admin_bp.get('/employee_list')
# @jwt_required()
def employee_list():
    try:
        # user_id=get_jwt_identity()
        # print(user_id)
        cursor = g.db.cursor(dictionary=True)
        
        # cursor.execute(f'SELECT id,firstname,lastname,email,gender FROM tbl_users WHERE id NOT IN({user_id})')
        cursor.execute('SELECT id,firstname,lastname,email,gender FROM tbl_users ORDER BY id ASC')
        user = cursor.fetchall()

        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@admin_bp.get('/employee_search')
@jwt_required()
def employee_search():
    try:
        user_id = get_jwt_identity()
        print(user_id)

        employee_search = request.json.get('employee_search')

        if not employee_search:
            return jsonify({'error': 'Employee search parameter is required'}), 400

        if len(employee_search) < 3:
            return jsonify({'error': 'Employee search parameter should have at least 3 characters'}), 400

        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT id, firstname, lastname, email, gender FROM tbl_users WHERE firstname LIKE '{employee_search}%' OR lastname LIKE '{employee_search}%' ")
        user = cursor.fetchone()

        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500