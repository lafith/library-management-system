from flask import render_template
from app import lbms_app


@lbms_app.route('/')
@lbms_app.route('/index')
def index():
    """View function for home page"""
    return render_template('home.html')
