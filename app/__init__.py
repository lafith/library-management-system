from flask import Flask

lbms_app = Flask(__name__)

from app import routes
