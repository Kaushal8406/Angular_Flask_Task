from flask import Flask ,g
import os
import mysql.connector
from datetime import timedelta
from flask_jwt_extended import JWTManager
from project.authetication import authetication_bp
# from project.admin import admin_bp
from project.user import user_bp
from flask_mail import Mail, Message
from flask_cors import CORS

app = Flask(__name__)
mail = Mail(app)
CORS(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jigoprajapati01@gmail.com'
app.config['MAIL_PASSWORD'] = 'aqjnxziomrcbnmyy'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
    program = g.db.cursor(dictionary=True)
    program.execute('SELECT * from tbl_user LIMIT 2')
    result = program.fetchall()
    for a in result:
      print(a)
    return('Hyperlink Infosystem in Rest API Project!')

@app.before_request
def before_request():
    g.db=mysql.connector.connect(
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        host=os.environ['MYSQL_HOST'],
        database=os.environ['MYSQL_DB']
    )
    print("Database Connected")
    return


@app.after_request
def after_request(response):
    g.db.close()
    print("Database Disconnected")
    return response

app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_BLACKLIST_ENABLAD'] = True
app.config['JWT_BLACKLIST_TOKEN_CKECKS']= ['access', 'refresh']

jwt = JWTManager(app)

app.register_blueprint(authetication_bp)

# app.register_blueprint(admin_bp)

app.register_blueprint(user_bp)