from flask import Blueprint,request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename


user_bp = Blueprint('user', __name__)


    



@user_bp.get('/user_coine_desc')
@jwt_required()
def user_coine():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute('SELECT email,coine FROM tbl_user ORDER BY coine DESC')
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404



@user_bp.get('/sub_categories/<id>')
@jwt_required()
def categories(id):
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f'SELECT * FROM tbl_sub_categories WhERE id = {id}')

        categories = cursor.fetchall()
        if not categories:
            return jsonify({'error': 'Sub categories Not Found'}),404

        cursor.execute(f"""SELECT tsc.id,tsc.sub_category_name FROM tbl_categories tc JOIN tbl_sub_categories tsc
                        ON tsc.category_id = tc.id WHERE tc.id = {id};""")
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    




@user_bp.get('/all_sub_categories')
@jwt_required()
def all_sub_categories():
    try:
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute('SELECT id,category_id,sub_category_name FROM tbl_sub_categories')
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@user_bp.get('/all_categories')
@jwt_required()
def all_ategories():
    try:
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute('SELECT id as categories_id,categories_name FROM tbl_categories')
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404



@user_bp.get('/product/<id>')
@jwt_required()
def product(id):
    try:
        cursor = g.db.cursor(dictionary=True)

        cursor.execute(f'SELECT id FROM tbl_sub_categories WHERE id = {id}')
        sub_categories = cursor.fetchall()
        if not sub_categories:
            return jsonify({'Message': 'Sub categories Not Found'}),404
     
        cursor.execute(f"""SELECT tp.sub_category_id,tp.id,ts.sub_category_name,tp.name,tp.image,tp.price,tp.quality,tp.description,tp.is_active FROM tbl_product tp
                        JOIN tbl_sub_categories ts ON ts.id = tp.sub_category_id WHERE ts.id = {id}""")
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 



@user_bp.get('/all_product')
@jwt_required()
def all_product():
    try:
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute(f"""SELECT tp.id as Product_id,tp.sub_category_id,ts.sub_category_name,tp.name,tp.image,tp.price,tp.quality,tp.description,tp.is_active FROM tbl_product tp
                        JOIN tbl_sub_categories ts ON ts.id = tp.sub_category_id""")
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404



@user_bp.post('/buyer_product/<p_id>')
@jwt_required()
def buyer_product(p_id):
    try:
        id = get_jwt_identity()

        p_quality = request.json.get('quality')
        quality = int(p_quality)
        cursor = g.db.cursor()
        cursor.execute(f'SELECT id, quality FROM tbl_product WHERE id = {p_id}')
        product = cursor.fetchone()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        product_id = product[0]
        existing_quality = product[1]
        product_value = int(existing_quality)

        if quality <= 0:
            return jsonify({'error': 'Product Are Not Define'}),400

        if quality > product_value:
            return jsonify({'error': 'Requested quality is not available'}), 400
        
        quality_buyes = product_value - quality
        print(quality_buyes)

        cursor.execute(f'SELECT coine FROM tbl_user WHERE id = {id}')
        coine = cursor.fetchone()
        balance = coine[0]

        Balance_coine  = quality * 100

        Data_Balance = balance - Balance_coine

        if Data_Balance < 0:
            return jsonify({'error': 'Coine Are Not Availeble'}),400
    
        cursor.execute(
            'INSERT INTO tbl_buyer (user_id, product_id, quality) VALUES (%s, %s, %s)',
            (id, product_id, quality))
        g.db.commit()

        cursor.execute('UPDATE tbl_product SET quality = %s WHERE id = %s', (quality_buyes,p_id))
        g.db.commit()

        cursor.execute('UPDATE tbl_user SET coine = %s WHERE id = %s', (Data_Balance,id))
        g.db.commit()

      
        return jsonify({'message': 'Product purchased successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 404





@user_bp.post('/user_invites/<id>')
@jwt_required()
def user_invites(id):
    try:
        sender_id = get_jwt_identity()
        cursor = g.db.cursor()

        cursor.execute(f'SELECT id,email FROM tbl_user WHERE id={id}')
        user = cursor.fetchone()
        reciver_id = user[0]

        if not user:
            return jsonify({'error': 'Not Found User'}),404

        invite = 1

        cursor.execute(
                'INSERT INTO tbl_user_invites (sender_id, reciver_id) VALUES (%s, %s)',
                (sender_id, reciver_id))
        cursor.execute('UPDATE tbl_user SET is_invite = %s WHERE id = %s', (invite,reciver_id))
        g.db.commit()

        return jsonify({"Message": "Successfully Invites"}),200

    except Exception as e:
        return jsonify({'error': str(e)}), 404




@user_bp.get('/all_user')
@jwt_required()
def all_user():
    try:
        id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute(f'SELECT id as user_id,email,is_invite FROM tbl_user WHERE id != {id}')
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    

@user_bp.get('/user')
@jwt_required()
def user():
    try:
        id = get_jwt_identity()
        
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute(f'SELECT id as user_id,email,profile_img,bio,coine FROM tbl_user WHERE id = {id}')
        
        user = cursor.fetchall()

        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    


@user_bp.post('/user_update')
@jwt_required()
def user_update():
    try:
        id = get_jwt_identity()

        image = request.json.get('image')
        bio = request.json.get('bio')


        if not image:
            return jsonify({'error': 'Image is required'}),404
        
        if not bio:
            return jsonify({'error': 'Image is required'}),404
        
        cursor = g.db.cursor()
     
        cursor.execute('UPDATE tbl_user SET bio = %s, profile_img = %s WHERE id = %s', (bio, image, id,))

        g.db.commit()
    
        return jsonify({"Message": "Successfully Update Profile"}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404



@user_bp.post('/sell_product')
@jwt_required()
def sell_product():
    try:
        id = get_jwt_identity()
        cursor = g.db.cursor()

        categories_id = request.json.get('categories_id')
        cursor.execute(f'SELECT id,categories_name FROM tbl_categories WHERE id= {categories_id}')
        categories = cursor.fetchone()   

        if not categories:
            return jsonify({'error': 'Category Not Found'}), 404
        
        
        cursor.execute(f"""SELECT tsb.id,tsb.category_id,tsb.sub_category_name FROM tbl_sub_categories tsb
                            JOIN tbl_categories tc ON tsb.category_id = tc.id WHERE tsb.category_id = {categories_id}""")
        
        sub_categories = cursor.fetchall()
       
        sub_categories_id = sub_categories[0][0]
       

        if not sub_categories:
            return jsonify({'error': 'Subcategory Not Found'}), 404
        
        name = request.json.get('name')
        image = request.json.get('image')
        price = request.json.get('price')
        price_a = float(price)


        if price_a <= 0:
            return jsonify({'error': 'Please Price Are Proper'}),400
        
        quality = request.json.get('quality')
        quality_a = float(quality)

        if quality_a <= 0:
            return jsonify({'error': 'Quality as a Proper'}),400
        
        description = request.json.get('description')

        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        if not image:
            return jsonify({'error': 'Image is required'}), 400
        
        if not price:
            return jsonify({'error': 'Price is required'}), 400
        
        if not quality:
            return jsonify({'error': 'Quality is required'}), 400
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        cursor.execute(
            'INSERT INTO tbl_product (user_id, name, image, price, quality, description, sub_category_id) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (id, name, image, price, quality, description, sub_categories_id,)
        )
        g.db.commit()

        return jsonify({'message': 'Product sold successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 404


@user_bp.get('/buy_product_list')
@jwt_required()
def buy_product_list():
    try:
        id = get_jwt_identity()
        
        cursor = g.db.cursor(dictionary=True)
     
        cursor.execute(f"""SELECT tb.id,tp.name,tb.quality FROM tbl_buyer tb JOIN tbl_product tp
                        ON tb.product_id = tp.id WHERE tb.user_id = {id}""")
        user = cursor.fetchall()
        return jsonify(user),200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    