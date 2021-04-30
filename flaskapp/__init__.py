import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates'
            )


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)

migrate = Migrate(app, db)
from flaskapp import routes
