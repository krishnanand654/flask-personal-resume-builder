import json
import os
import firebase_admin
import base64
from flask import Flask, render_template, jsonify, request, session, url_for,redirect
from flask_login import LoginManager, login_user, login_required, UserMixin
from dotenv import load_dotenv
from firebase_admin import db

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

base64_service_account_key = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_BASE64')
service_account_key_json = base64.b64decode(base64_service_account_key).decode('utf-8')
service_account_info = json.loads(service_account_key_json)

app.db_url = os.getenv("DB_URL")


cred_obj = firebase_admin.credentials.Certificate(service_account_info)
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':app.db_url
	})

ref=db.reference("/")

login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)        


resume_data={}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        provided_secret_key = request.form.get('secret_key')
        print(app.secret_key)
        if provided_secret_key == app.secret_key:
            user = User(1) 
            login_user(user)
            session['logged_in'] = True
            return redirect(url_for('update'))
        else:
            return 'Invalid secret key. Please try again.'  
    return render_template('login.html')

@app.route('/')
def index():

    two_page = request.args.get('two_page')
    color = request.args.get('color')
    
    # with open('resume_data.json','r') as file_object:
    #     resume_data = json.load(file_object)    

    resume_data = ref.get()
  
    resume_data['projects'] = sorted(resume_data['projects'], key=lambda x: x['date'], reverse=True)

    return render_template('index.html', resume=resume_data, two_page=two_page, color=color)



@app.route('/update',methods=['GET','POST'])
@login_required
def update():
    two_page = request.args.get('two_page')
    color = request.args.get('color')
    
    with open('resume_data.json','r') as file_object:
        resume_data = json.load(file_object)    
  
    resume_data['projects'] = sorted(resume_data['projects'], key=lambda x: x['date'], reverse=True)

    if request.method == 'POST':
        data = request.form
        for key,val in data.items():
            if key == 'soft_skills':
                resume_data['soft_skills'] = val
            elif key == 'summary_edit':
                resume_data['objective'] = val
            elif key == 'language_edit':
                resume_data['skills']['languages'] = val
            elif key == 'technologies_edit':
                resume_data['skills']['technologies'] = val
            elif key == 'tools_edit':
                resume_data['skills']['tools'] = val
            # with open(' resume_data.json','w') as file_object:
            #     json.dump(resume_data,file_object)
        ref.set(resume_data)
  
    return render_template('update.html', resume=resume_data, two_page=two_page, color=color)

@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))


@app.route('/data')
def data():
    return jsonify(resume_data)

