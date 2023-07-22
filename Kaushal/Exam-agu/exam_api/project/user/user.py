from flask import Blueprint,request, jsonify, g
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_mail import Mail, Message

user_bp = Blueprint('user', __name__)

def is_user(user_id):
    cur = g.db.cursor()
    cur.execute(f"select role from tbl_user where id={user_id}")
    user = cur.fetchone()
    if user:
        if user[2] == 'user':
            return True
        return False
    


def is_admin(user_id):
    cur = g.db.cursor()
    cur.execute(f"select role from tbl_user where id={user_id}")
    user = cur.fetchone()
    if user:
        if user[2] == 'admin':
            return True
        return False


@user_bp.post('/complain')
@jwt_required()
def complain():
    try:
        id =get_jwt_identity()
        
        data = request.json
        subject = data.get('subject')
        description = data.get('description')
        complain_date = data.get('complain_date')
        complain_time = data.get('complain_time')

        if not subject:
            return jsonify({"message": "Invalid or missing subject"}), 400

        if not description:
            return jsonify({'message': 'Description is required'}), 400

        if not complain_date:
            return jsonify({'message': 'Complain_date is required'}), 400

        if not complain_time:
            return jsonify({'message': 'Complain_time is required'}), 400

        cursor = g.db.cursor()
        cursor.execute(
            'INSERT INTO tbl_complains (user_id, subject, description, complain_date, complain_time) VALUES (%s, %s, %s, %s, %s)',
            (id, subject, description, complain_date, complain_time))
        g.db.commit()

        msg = Message(
            'Complain Info',
            sender='jigoprajapati01@gmail.com',
            recipients=['kaushalprajapati@hyperlinkinfosystem.net.in']
        )
        cursor.execute(f'SELECT * FROM tbl_user WHERE id={id}')
        user = cursor.fetchone()
        RegId = user[1]
        print("aaaaaaaaaaaaaaaaaaaaaa",RegId)
        msg.body = f'Complain_Subject: {subject}\n\nComplain_Description: {description}\n\nComplain_Date: {complain_date}\n\nTemporary Complain_Time: {complain_time}\n\nRegId:{RegId}'
        
        from project import mail
        mail.send(msg)

        return jsonify({'message': 'Successfully submitted complaint'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@user_bp.get('/complaint_list')
@jwt_required()
def complaint_list():
     id = get_jwt_identity()
          
     cursor = g.db.cursor(dictionary=True)
     cursor.execute(f'SELECT id,subject,description,complain_date,complain_time,complain_status FROM tbl_complains WHERE user_id = {id}')
     user = cursor.fetchall()

     for users in user:
            users['complain_time'] = str(users['complain_time'])
            users['complain_date'] = str(users['complain_date']) 

     return jsonify(user),200



@user_bp.get('/user_name')
@jwt_required()
def user_name():
     id = get_jwt_identity()
     cursor = g.db.cursor(dictionary=True)
     cursor.execute(f'SELECT username FROM tbl_user WHERE id ={id}')
     user = cursor.fetchone()
     return jsonify(user),200




@user_bp.get('/user_list')
@jwt_required()
def user_list():
     cursor = g.db.cursor(dictionary=True)
     cursor.execute('SELECT Regid,username,name,email,is_verify FROM tbl_user')
     user = cursor.fetchall()
     return jsonify(user),200



@user_bp.get('/complain_list_admin')
@jwt_required()
def complain_list_admin():
     cursor = g.db.cursor(dictionary=True)
     cursor.execute('SELECT user_id,id,subject,description,complain_date,complain_time,complain_status FROM tbl_complains')
     user = cursor.fetchall()

     for users in user:
            users['complain_time'] = str(users['complain_time'])
            users['complain_date'] = str(users['complain_date']) 
   
     return jsonify(user),200


@user_bp.patch('/complain_status/<id>')
@jwt_required()
def complain_status(id):
     try:
        cursor = g.db.cursor()
      
        cursor.execute(f'SELECT * FROM tbl_complains WHERE id ={id}')
        user = cursor.fetchall()
        if not user:
             return jsonify({'error': 'Complain Not found'}),404

        cursor.execute(f"UPDATE tbl_complains SET complain_status = 'Complete' WHERE id = {id}")
        g.db.commit()
        return jsonify({'Message': 'Complain is Successful work'}),201
     
     except Exception as e:
        return jsonify({'error': str(e)}), 404

