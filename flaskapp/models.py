import datetime
from flask_login import UserMixin

from flaskapp import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    image = db.Column(db.Text(), default='index.png')
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    posts = db.relationship('Post', backref='user', lazy=True)





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_name = db.Column(db.String(100))
    epoch_image = db.Column(db.Text)
    hypnogram_image = db.Column(db.Text)
    pie_image = db.Column(db.Text)
    result1 = db.Column(db.Text)
    result2 = db.Column(db.Text)
    post_time = db.Column(db.DateTime(), index=True, default=datetime.datetime.now)
