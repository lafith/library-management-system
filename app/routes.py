from flask import render_template, request
from flask import flash, redirect, url_for
from app import lbms_app, db, bcrypt
from app.models import Library
from app.forms import RegisterForm


# This route is for showing 'Home' page
@lbms_app.route('/')
@lbms_app.route('/index')
def index():
    """View function for home page"""
    return render_template('home.html')


@lbms_app.route('/about')
def about():
    """View function for About Us page"""
    return render_template('about.html')


@lbms_app.route('/register', methods=['GET', 'POST'])
def register():
    """View function for Registration page"""
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = bcrypt.generate_password_hash(
            form.password.data
            ).decode('utf-8')
        library = Library(name=name, email=email, password=password)
        db.session.add(library)
        db.session.commit()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@lbms_app.route('/login', methods=['GET', 'POST'])
def login():
    """View function for login page"""
    return render_template('login.html')
