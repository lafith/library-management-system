from flask import Flask
from config import Config

lbms_app = Flask(__name__)
lbms_app.config.from_object(Config)

from app import routes
