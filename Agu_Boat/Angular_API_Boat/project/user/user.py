from flask import Blueprint, request, jsonify, g
from flask_jwt import jwt_required
from flask_jwt_extended import jwt_required,get_jwt_identity

user_bp = Blueprint('user', __name__)



def is_user(user_id):
    cur = g.db.cursor()
    cur.execute(f"select role from tbl_user where id={user_id}")
    user = cur.fetchone()
    if user:
        if user[0] == 'user':
            return True
        return False
    


def is_admin(user_id):
    cur = g.db.cursor()
    cur.execute(f"select role from tbl_user where id={user_id}")
    user = cur.fetchone()
    if user:
        if user[0] == 'admin':
            return True
        return False



@user_bp.post('/add_boat')
@jwt_required()
def add_boat():
    try:
        user_id = get_jwt_identity()
        boatname = request.json.get('boatname')
        boatsize = request.json.get('boatsize')
        boatcapacity = request.json.get('boatcapacity')

        if not boatname:
            return jsonify({"message": "Boat_name are insert"}), 400
        
        if not boatsize:
            return jsonify({"message": "Boat_size are insert"}), 400
        
        if not boatcapacity:
            return jsonify({"message": "Boat_capacity are insert"}), 400
        
        cursor = g.db.cursor()
        cursor.execute('INSERT INTO tbl_boat (user_id, boatname, boatsize,boatcapacity) VALUES (%s, %s, %s, %s)',
                    (user_id, boatname, boatsize,boatcapacity))
        g.db.commit()  
        return jsonify({'message': 'Boat are successfully inserted'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   



@user_bp.get('/boat_list')
@jwt_required()
def boat_list():
        # user_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        # cursor.execute(f"""SELECT COUNT(tb.id) as count,tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_sensor FROM tbl_boat tb
        #                 JOIN tbl_user tu ON tb.user_id = tu.id 
        #                 """)
        cursor.execute('SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_sensor FROM tbl_boat tb;')
        user =cursor.fetchall()
        return jsonify(user),200


@user_bp.get('/boat_list_user')
@jwt_required()
def boat_list_user():
        user_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_sensor FROM tbl_boat tb
                        JOIN tbl_user tu ON tb.user_id = tu.id WHERE tu.id = {user_id}""")
        user =cursor.fetchall()
        return jsonify(user),200



@user_bp.get('/boat_count')
@jwt_required()
def boat_count():
        user_id = get_jwt_identity()

        if not is_admin(user_id):
            return jsonify({"error":"Unauthrized Access"}),401
        
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(id) as Total_Boat FROM tbl_boat')
        user =cursor.fetchall()
        return jsonify(user),200



@user_bp.post('/edit_boat/<id>')
@jwt_required()
def edit_boat(id):
    try:
        updated_by = get_jwt_identity()

        edit_boatname = request.json.get('edit_boatname')
        edit_boatsize = request.json.get('edit_boatsize')
        edit_boatcapacity = request.json.get('edit_boatcapacity')

        if not edit_boatname:
            return jsonify({"message": "Boat_name is not provided"}), 400

        if not edit_boatsize:
            return jsonify({"message": "Boat_size is not provided"}), 400

        if not edit_boatcapacity:
            return jsonify({"message": "Boat_capacity is not provided"}), 400

        cursor = g.db.cursor()
        cursor.execute("UPDATE tbl_boat SET updated_by = %s, boatname = %s, boatsize = %s, boatcapacity = %s WHERE id = %s",
                       (updated_by, edit_boatname, edit_boatsize, edit_boatcapacity, id))
        g.db.commit()
        return jsonify({'message': 'Boat has been updated'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# is_sensor = 'Sensor_install'

@user_bp.post('/add_sensor/<boat_id>')
@jwt_required()
def add_sensor(boat_id):
    try:
        cursor = g.db.cursor()
        cursor.execute(f'SELECT * FROM tbl_boat WHERE id={boat_id}')
        user = cursor.fetchone()
        print(user)

        if not user:
            return jsonify({"message": "Boat Are Not Availble"}), 400
        
        pressure = request.json.get('pressure')
        humidity = request.json.get('humidity')
        temperature = request.json.get('temperature')

        if not pressure:
            return jsonify({"message": "Pressure are insert"}), 400
        
        if not humidity:
            return jsonify({"message": "Humidity are insert"}), 400
        
        if not temperature:
            return jsonify({"message": "Temperature are insert"}), 400
        
        
        cursor.execute('INSERT INTO tbl_sensor (boat_id, pressure, humidity, temperature) VALUES (%s, %s, %s, %s)',
                    (boat_id, pressure, humidity, temperature))
        cursor.execute(f"UPDATE tbl_boat SET is_sensor = 'Sensor_install' WHERE id ={boat_id}")
        g.db.commit()  
        return jsonify({'message': 'Sensor are successfully inserted'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   


@user_bp.get('/sensor_list')
@jwt_required()
def sensor_list():
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT id,boat_id,pressure,humidity,temperature FROM tbl_sensor')
        user =cursor.fetchall()
        return jsonify(user),200


@user_bp.get('/boat_search')
@jwt_required()
def boat_search():
    try:
        cursor = g.db.cursor(dictionary=True)
        search = request.json.get("search_boat")
        cursor.execute(f"SELECT boatname, boatsize, boatcapacity FROM tbl_boat WHERE boatname OR boatsize OR boatcapacity LIKE '{search}%' ")
        user =cursor.fetchall()
        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@user_bp.get('/list_user')
@jwt_required()
def list_user():
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("SELECT id,firstname,lastname,email,is_active FROM tbl_user")
        user =cursor.fetchall()
        return jsonify(user),200



@user_bp.get('/user_count')
@jwt_required()
def user_count():
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT COUNT(id) as count FROM tbl_user')
        user =cursor.fetchall()
        return jsonify(user),200






@user_bp.post('/edit_sensor/<id>')
@jwt_required()
def edit_sensor(id):
    try:
        updated_by = get_jwt_identity()
        pressure = request.json.get('pressure')
        humidity = request.json.get('humidity')
        temperature = request.json.get('temperature')

        if not pressure:
            return jsonify({"message": "pressure is not provided"}), 400

        if not humidity:
            return jsonify({"message": "humidity is not provided"}), 400

        if not temperature:
            return jsonify({"message": "temperature is not provided"}), 400

        cursor = g.db.cursor()
        cursor.execute("UPDATE tbl_sensor SET updated_by = %s, pressure = %s, humidity = %s, temperature = %s WHERE boat_id = %s",
                       (updated_by, pressure, humidity, temperature, id))
        g.db.commit()
        return jsonify({'message': 'Sensor has been updated'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@user_bp.get('/name')
@jwt_required()
def name():
        user_id = get_jwt_identity()       
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f'SELECT firstname FROM tbl_user WHERE id = {user_id}')
        user =cursor.fetchall()
        return jsonify(user),200


@user_bp.delete('/sensor_delete/<id>')
@jwt_required()
def sensor_delete(id):
        cursor = g.db.cursor()
        cursor.execute(f'DELETE FROM tbl_sensor WHERE boat_id={id}')
        cursor.execute(f"UPDATE tbl_boat SET is_sensor = 'Sensor_not_install' WHERE id ={id}")
        g.db.commit()
        return jsonify({'Message' : 'Delete The Sensor'}),200


@user_bp.delete('/boat_delete/<id>')
@jwt_required()
def boat_delete(id):
        cursor = g.db.cursor()
        cursor.execute(f'DELETE FROM tbl_boat WHERE id={id}')
        g.db.commit()
        return jsonify({'Message' : 'Delete The Boat'}),200


@user_bp.delete('/user_delete/<id>')
@jwt_required()
def user_delete(id):
        cursor = g.db.cursor()
        cursor.execute(f'DELETE FROM tbl_user WHERE id={id}')
        g.db.commit()
        return jsonify({'Message' : 'Delete The User'}),200



# cursor.execute(f"SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_active,ts.pressure,ts.humidity,ts.temperature,tb.is_delete,ts.id as s_id FROM tbl_boat as tb JOIN tbl_sensor AS ts ON tb.id = ts.boat_id WHERE pressure >= {search}")
     

# @user_bp.post('/sensor_search')
# def sensor_search():
#     try:
#         cursor = g.db.cursor(dictionary=True)
#         search = request.json.get("sensor_search")
#         cursor.execute(f"""
#         SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_active,ts.pressure,ts.humidity,ts.temperature,tb.is_delete,ts.id as s_id FROM tbl_boat as tb JOIN tbl_sensor AS ts ON tb.id = ts.boat_id WHERE ts.pressure OR ts.humidity OR ts.temperature OR tb.boatname OR tb.boatsize OR tb.boatcapacity LIKE '{search}%'
#         """)
#         sensors = cursor.fetchall()
#         return jsonify(sensors), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@user_bp.post('/sensor_search')
def sensor_search():
    try:
        cursor = g.db.cursor(dictionary=True)
        search = request.json.get("sensor_search")

        cursor.execute(f"""
        SELECT tb.id, tb.boatname, tb.boatsize, tb.boatcapacity, tb.is_active, ts.pressure, ts.humidity,
               ts.temperature, tb.is_delete, ts.id AS s_id
        FROM tbl_boat AS tb
        JOIN tbl_sensor AS ts ON tb.id = ts.boat_id
        WHERE ts.pressure LIKE %s
          OR ts.humidity LIKE %s
          OR ts.temperature LIKE %s
          OR tb.boatname LIKE %s
          OR tb.boatsize LIKE %s
          OR tb.boatcapacity LIKE %s
        """, (f'{search}%', f'{search}%', f'{search}%', f'{search}%', f'{search}%', f'{search}%'))


        sensors = cursor.fetchall()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@user_bp.post('/user_active/<id>')
def user_active(id):
        cursor = g.db.cursor()
        cursor.execute(f'UPDATE tbl_user SET is_verify = 1, is_active = 1 WHERE id = {id}')
        g.db.commit()
        return jsonify({'Message' : 'User are Active'}),200




@user_bp.post('/user_deactive/<id>')
def user_deactive(id):
        cursor = g.db.cursor()
        cursor.execute(f'UPDATE tbl_user SET is_verify = 0, is_active = 0 WHERE id = {id}')
        g.db.commit()
        return jsonify({'Message' : 'User are Deactive'}),200



@user_bp.get('/boat_count_user')
@jwt_required()
def boat_count_user():
        id = get_jwt_identity()     
        
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f'SELECT COUNT(id) as count FROM tbl_boat WHERE user_id = {id}')
        user =cursor.fetchall()
        return jsonify(user),200




@user_bp.post('/Pressure_50')
# @jwt_required()
def Pressure_50():
    try:
        cursor = g.db.cursor(dictionary=True)
        # search = request.json.get("sensor_search")
        cursor.execute(f"SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_active,ts.pressure,ts.humidity,ts.temperature,tb.is_delete,ts.id as s_id FROM tbl_boat as tb JOIN tbl_sensor AS ts ON tb.id = ts.boat_id WHERE pressure > {199}")
        sensors = cursor.fetchall()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@user_bp.get('/Pressure_100')
# @jwt_required()
def Pressure_100():
    try:
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute(f"SELECT tb.id,tb.boatname,tb.boatsize,tb.boatcapacity,tb.is_active,ts.pressure,ts.humidity,ts.temperature,tb.is_delete,ts.id as s_id FROM tbl_boat as tb JOIN tbl_sensor AS ts ON tb.id = ts.boat_id")
        sensors = cursor.fetchall()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@user_bp.post('/sensor_pop/<id>')
# @jwt_required()
def sensor_pop(id):
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT ts.pressure,ts.humidity,ts.temperature FROM tbl_sensor ts JOIN tbl_boat tb 
                        ON ts.boat_id = tb.id WHERE tb.id = {id}""")
        sensors = cursor.fetchall()
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500






# @user_bp.post('/comment_reply')
# @jwt_required()
# def comment_reply():
#     try:
#         id = get_jwt_identity()
#         data = request.form
#         user_id = id
#         comment_id = data.get('comment_id','')
#         comment_reply = data.get('comment_reply','')

#         cursor = g.db.cursor()

#         if not comment_id:
#             return jsonify({"message": "comment_id are insert"}), 400
        
#         if not comment_reply:
#             return jsonify({"message": "comment_reply are insert"}), 400
        
        
#         cursor.execute('INSERT INTO tbl_comment_reply (user_id,comment_id,comment_reply) VALUES (%s,%s,%s)',(user_id,comment_id,comment_reply))
#         g.db.commit()  
#         return jsonify({'message': 'comment reply successfully inserted'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# # --------------------------------------audio_data------------------------------
# #allll


# @user_bp.get('/audio_data')
# @jwt_required()
# def audio_data():
#         cursor = g.db.cursor(dictionary=True)
#         cursor.execute('SELECT music_type,music_img,music FROM tbl_audio WHERE is_active=1 AND is_delete=0')
#         user =cursor.fetchall()
#         return jsonify(user),200
      


# #-----------------------------------------rock-------------------------------------
# #music_type == rock


# @user_bp.get('/rock')
# @jwt_required()
# def rock():

#         cursor = g.db.cursor(dictionary=True)
       
#         cursor.execute("SELECT music_img,music FROM tbl_audio WHERE music_type='rock'")
#         # cursor.execute("SELECT music_img,music FROM tbl_audio WHERE music_type='country_music'")
#         user =cursor.fetchall()
#         return jsonify({
#             'rock' : user,
#             # 'country_music' :user
#         })


# #----------------------------------------------country_music----------------------------------------------------------------  

# @user_bp.get('/country_music')
# @jwt_required()
# def country_music():
#         cursor = g.db.cursor(dictionary=True)
#         cursor.execute("SELECT music_img,music FROM tbl_audio WHERE music_type='country_music'")
#         user =cursor.fetchall()
#         return jsonify({ 
#             'country_music' :user
#         })


# #------------------------------classical_music-----------------------------------------

# @user_bp.get('/classical_music')
# @jwt_required()
# def classical_music():
#         cursor = g.db.cursor(dictionary=True)
#         cursor.execute("SELECT music_img,music FROM tbl_audio WHERE music_type='classical_music'")
#         user =cursor.fetchall()
#         return jsonify({ 
#             'classical_music' :user
#         })




# #-----------------------------------------------------------------------------------------------------------

# @user_bp.get('/audio_des')
# @jwt_required()
# def audio_des():
#      try:
#         id = request.form.get('id','')
#         cursor = g.db.cursor(dictionary=True)
#         cursor.execute('SELECT music_type,music_img,music,comment_count, description FROM tbl_audio WHERE id=%s AND is_active=1 AND is_delete=0', (id,))
#         user =cursor.fetchall()
#         return jsonify(user),200
#      except Exception as e:
#         return jsonify({'error': str(e)}), 500



# @user_bp.get('/comment_user')
# @jwt_required()
# def comment_user():
#      try:
#         id = request.form.get('id','')
#         cursor = g.db.cursor(dictionary=True)
#         cursor.execute('SELECT tu.profile_img,tu.name,tc.comment,tcr.comment_reply FROM tbl_audio ta JOIN tbl_comment tc ON ta.id = tc.audio_id JOIN tbl_user tu ON tc.user_id = tu.id JOIN tbl_comment_reply tcr ON tc.id = tcr.comment_id WHERE ta.id=%s', (id,))
#         user =cursor.fetchall()
#         return jsonify(user),200
#      except Exception as e:
#         return jsonify({'error': str(e)}), 500

