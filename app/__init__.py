from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap


lbms_app = Flask(__name__)
lbms_app.config.from_object(Config)
Bootstrap(lbms_app)
# database setup
db = SQLAlchemy(lbms_app)
migrate = Migrate(lbms_app, db)

bcrypt = Bcrypt(lbms_app)

from app import routes
