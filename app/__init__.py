from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# setup the app
app = Flask(__name__)
app.config.from_object(Config)
# database setup
db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)

from app import routes
