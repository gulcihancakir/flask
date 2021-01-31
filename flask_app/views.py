import base64
import csv
import os
from pathlib import Path

from flask import (Flask, Response, flash, redirect, render_template, request,
                   session, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user,UserMixin)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sys

import prediction



app = Flask(__name__)
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates'
            )

UPLOAD_FOLDER = './temp'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db=SQLAlchemy(app)
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)

global f

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == "POST":

        for i in range(1, 4):

            fl = request.files['fname'+str(i)]
            filename = secure_filename(fl.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'])
        
            global f

            f, extension = os.path.splitext(filename)
      
            fl.save(file_path+"/"+filename)

      

        prediction.predict_and_plot_sstaging(file_path, f)
        prediction.predict_and_plot_sdisease(file_path, f)

        return render_template('index.html', result=prediction.figure, result1=prediction.figure2, result2=prediction.figure3,
                               result_txt=prediction.read_file, result_txt2=prediction.read_file2)
    return render_template('index.html')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Geçersiz kullanıcı ya da parola')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('profil'))
    return render_template("login.html")



@app.route("/signup",methods=['GET', 'POST'])
def signup():
    if request.method=="POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Kullanıcı mevcut')
            return redirect(url_for('signup'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))
    return render_template("signup.html")


@app.route("/profil")
@login_required
def profil():
    return render_template("profil.html",name=current_user.name)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
