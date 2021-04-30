from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import ValidationError

from flaskapp.models import User


class UserForm(FlaskForm):
    email = EmailField('email', [validators.Length(min=6, max=35)])
    name = StringField('name', [validators.Length(min=2, max=25)])
    password = PasswordField('password', [validators.DataRequired()])


class UserLoginForm(FlaskForm):
    email = EmailField('email')
    password = PasswordField('password', [validators.DataRequired()])


class UserEditFrom(FlaskForm):
    email = EmailField('email', [validators.Length(min=6, max=35)])
    name = StringField('name', [validators.Length(min=2, max=25)])
    image = FileField('image', validators=[
                      FileAllowed(['png', 'jpg', 'jpeg'])])
    password = PasswordField('password', [validators.DataRequired()])
    password_new = PasswordField('password_new')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email hesabı mevcut!!!')
