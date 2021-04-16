from flask import render_template, request
from app import lbms_app
from app.forms import RegisterForm


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


@lbms_app.route('/register', methods=['GET', 'POST'])
def register():
    """View function for Registration page"""
    form = RegisterForm(request.form)
    return render_template('register.html', form=form)
