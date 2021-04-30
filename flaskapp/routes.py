
import os
import secrets

from flask import (flash, redirect, render_template, request,
                   url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# import flaskapp.prediction
from flaskapp import app, prediction
from flaskapp.forms import UserEditFrom, UserForm, UserLoginForm
from flaskapp.models import Post, User

db = SQLAlchemy(app)

migrate = Migrate(app, db)
app.config['SECRET_KEY'] = 'secret-key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:toor@localhost/flask_app'
db.init_app(app)
UPLOAD_FOLDER = './flaskapp/temp'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
global f


@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == "POST":

        for i in range(1, 4):

            fl = request.files['fname'+str(i)]
            filename = secure_filename(fl.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'])
            print(UPLOAD_FOLDER)

            global f

            f, extension = os.path.splitext(filename)

            fl.save(file_path+"/"+filename)

        print(current_user.is_authenticated)
        prediction.predict_and_plot_sstaging(file_path, f)
        prediction.predict_and_plot_sdisease(file_path, f)

        if current_user.is_authenticated == True:
            new_post = Post(post_name=f, epoch_image="images/"+f+"_epochs.png", hypnogram_image="images/"+f+"_hypno.png",
                            pie_image="images/"+f+"_pie.png", result1=prediction.info, result2=prediction.info1,
                            user_id=current_user.id)

            db.session.add(new_post)
            db.session.commit()
        
        return render_template('index.html', result=prediction.figure, result1=prediction.figure2, result2=prediction.figure3,
                               result_txt=prediction.info, result_txt2=prediction.info1)
    return render_template('index.html')


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=['GET', 'POST'])
def login():

    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(form.email.data)
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Geçersiz kullanıcı adı ya da parola')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('profil'))

    return render_template("login.html", form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():

    form = UserForm()

    if form.validate_on_submit():
        print("hello")

        user = User.query.filter_by(email=form.email.data).first()
        print("user",user)

        if user:
            flash('Kullanıcı mevcut')

            return redirect(url_for('signup'))
        new_user = User(email=form.email.data, password=generate_password_hash(form.password.data, method='sha256'), name=form.name.data,
                        )
        print(new_user)
        print(User)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)


def save(image):
    random_hex = secrets.token_hex(8)
    f, extension = os.path.splitext(image.filename)
    image_filename = random_hex+extension
    image_path = os.path.join(
        app.root_path, 'static/images/profil_picture', image_filename)
    print(app.root_path)
    image.save(image_path)
    return image_filename

# @app.route("/user_edit",methods=['GET','POST'])
# def user_edit():
#     form = UserEditFrom()
#     if form.validate_on_submit():
#         if form.image.data:
#             image_file=save(form.image.data)

#             current_user.image=image_file
#         current_user.name=form.name.data
#         current_user.email=form.email.data
#         current_user.password=generate_password_hash(form.password.data,method='sha256')
#         db.session.commit()
#     elif request.method == 'GET':
#         form.name.data = current_user.name
#         form.email.data = current_user.email
#         form.password.data = current_user.password
#     return render_template('user_edit.html',
#                            form=form)
@app.route("/profil", methods=['GET', 'POST'])
@login_required
def profil():
    posts = Post.query.filter_by(user_id=current_user.id)
    posts = posts.paginate(per_page=2)
    
    user = User.query.filter_by(id=current_user.id).first()
    form = UserEditFrom()

    if form.validate_on_submit():
        print(check_password_hash(current_user.password, form.password.data))
        if check_password_hash(current_user.password, form.password.data):
            if form.image.data:
                print(form.image.data)
                image_file = save(form.image.data)
                print(image_file)
                current_user.image = image_file
            current_user.name = form.name.data
            current_user.email = form.email.data
            # current_user.password = generate_password_hash(
            #     form.password_new.data, method='sha256')
            db.session.commit()
            flash('Hesap Bilgileri Güncellendi')
            return redirect(url_for('profil'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.password.data = current_user.password

    image = url_for(
        'static', filename='images/profil_picture/'+current_user.image)

    return render_template("profil.html", posts=posts, user=user, image=image, form=form)


@app.route("/profil/post/detail/<int:pk>")
def post_detail(pk):
    post = Post.query.filter_by(id=pk).first()

    return render_template("profilpost_detail.html", post=post)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
