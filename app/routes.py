from flask import render_template
from app import lbms_app


# This route is for showing 'Home' page
@lbms_app.route('/')
@lbms_app.route('/index')
def index():
    """View function for home page"""
    return render_template('home.html')


# This route is for showing 'About Us' type information
@lbms_app.route('/about')
def about():
    """View function for About Us page"""
    return render_template('about.html')
