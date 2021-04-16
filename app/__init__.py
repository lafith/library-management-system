from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


lbms_app = Flask(__name__)
lbms_app.config.from_object(Config)

# database setup
db = SQLAlchemy(lbms_app)
migrate = Migrate(lbms_app, db)

bcrypt = Bcrypt(lbms_app)

from app import routes
