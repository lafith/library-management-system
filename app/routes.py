from flask import render_template, request, session
from flask import flash, redirect, url_for
from app import lbms_app, db, bcrypt
from app.models import Library, User
from app.forms import RegisterForm, BookForm
from functools import wraps


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
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        # Search database for the entered email
        l=Library.query.filter_by(email=email).first()
        if l:
            # Checking password
            password_candidate = request.form['password']
            if bcrypt.check_password_hash(l.password,password_candidate):
                session['logged_in'] = True
                session['email'] = email
                flash(f'You have been logged in!','success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


def is_logged_in(f):
    """This function will check if user is logged in"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@lbms_app.route('/logout')
@is_logged_in
def logout():
    """view function for logout tab"""
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@lbms_app.route('/dashboard')
@is_logged_in
def dashboard():
    """view function for dashboard page of each library"""
    return render_template('dashboard.html')


@lbms_app.route('/users')
@is_logged_in
def users():
    """View function for user management page"""
    l = Library.query.filter_by(email=session['email']).first()
    all_users = User.query.filter_by(library=l)
    return render_template('users.html', users=all_users)


@lbms_app.route('/add_user', methods=['GET', 'POST'])
@is_logged_in
def add_user():
    """View function to add user into database"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        l = Library.query.filter_by(email=session['email']).first()
        user = User(name=name, email=email, phone=phone, library=l)
        db.session.add(user)
        db.session.commit()
        flash("New user is added","success")
        return redirect(url_for('users'))

@lbms_app.route('/update', methods = ['GET', 'POST'])
@is_logged_in
def update():
    """View function for updating user info"""
    if request.method == 'POST':
        user = User.query.get(request.form.get('id'))
 
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
 
        db.session.commit()
        flash("User Information Updated Successfully")
 
        return redirect(url_for('users'))


@lbms_app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    """View function to remove entries from User table"""
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User Deleted Successfully")
    return redirect(url_for('users'))

@lbms_app.route('/books')
@is_logged_in
def books():
    """View function for user management page"""
    return render_template('books.html')

@lbms_app.route('/add_book', methods=['GET', 'POST'])
@is_logged_in
def add_book():
    """View function to add user into database"""
    form=BookForm(request.form)
    return redirect(url_for('users'),form=form)