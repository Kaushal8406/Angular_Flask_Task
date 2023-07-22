# from flask import Blueprint, request, jsonify,g
# from flask_jwt import jwt_required
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from werkzeug.utils import secure_filename
# import os


# admin_bp = Blueprint('admin', __name__)

# @admin_bp.post('/audio')
# def audio():
#     try:
#         data = request.form
#         music_type = data.get('music_type', '')
#         music_img = request.files['image']
#         music = data.get("music", '')
#         description = data.get("description", '')

#         if music_type not in ['rock', 'country_music', 'classical_music']:
#             return jsonify({"message": "music_type must be rock, cuntry_music or classical_music "}), 400
        
#         if not music:
#             return jsonify({'error': 'Music are Required'}), 400
        
#         if not music_type:
#             return jsonify({'error': 'Music_Type are Required'}), 400
        
#         if not music_img:
#             return jsonify({'error': 'No Image selected'}), 400
        
#         filename = secure_filename(music_img.filename)
#         music_img.save(os.path.join('project/media', filename))
#         cursor = g.db.cursor()
        
#         cursor.execute('INSERT INTO tbl_audio (music_type,music_img, music,description) VALUES (%s, %s, %s, %s)',
#                     (music_type,secure_filename(music_img.filename),music,description))
#         g.db.commit()  
#         return jsonify({'message': 'Music are successfully inserted'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @admin_bp.post('/image')
# def image():
#     try:
#         data = request.form
#         image = request.files['image']
#         image_titel = data.get("image_titel", '')
#         image_description = data.get("image_description", '')

#         if not image:
#             return jsonify({'error': 'No Image selected'}), 400
        
#         if not image_titel:
#             return jsonify({'error': 'image_titel are Required '}), 400
        
#         if not image_description:
#             return jsonify({'error': 'image_description are Required'}), 400
        
#         filename = secure_filename(image.filename)
#         image.save(os.path.join('project/media', filename))
#         cursor = g.db.cursor()
        
#         cursor.execute('INSERT INTO tbl_image (image,image_titel,image_description) VALUES (%s, %s, %s)',
#                     (secure_filename(image.filename),image_titel,image_description))
#         g.db.commit()  
#         return jsonify({'message': 'image Data are successfully inserted'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @admin_bp.post('/video')
# def video():
#     try:
#         data = request.form
#         video =  data.get("video", '')

#         video_titel = data.get("video_titel", '')
#         video_description = data.get("video_description", '')

#         if not video:
#             return jsonify({'error': 'video are Required'}), 400
        
#         if not video_titel:
#             return jsonify({'error': 'video_titel are Required '}), 400
        
#         if not video_description:
#             return jsonify({'error': 'video_description are Required'}), 400

    
#         cursor = g.db.cursor()
        
#         cursor.execute('INSERT INTO tbl_video (video,video_titel,video_description) VALUES (%s, %s, %s)',
#                     (video,video_titel,video_description))
#         g.db.commit()  
#         return jsonify({'message': 'video Data are successfully inserted'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



# @admin_bp.post('/link')
# def link():
#     try:
#         data = request.form
#         url =  data.get('url', '')

#         cursor = g.db.cursor()
        
#         cursor.execute('INSERT INTO tbl_link (url) VALUES (%s)',(url,))
#         g.db.commit()  
#         return jsonify({'message': 'Link successfully inserted'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500




   
