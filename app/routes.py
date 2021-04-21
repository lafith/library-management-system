from flask import render_template, request, session
from flask import flash, redirect, url_for
from app import lbms_app, db, bcrypt
from app.models import Library, User, Book
from app.forms import RegisterForm, LoginForm
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
        print(form.email)
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
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        session['logged_in'] = True
        session['email'] = email
        flash('You have been logged in!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html',form=form)


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
    library = Library.query.filter_by(email=session['email']).first()
    all_users = User.query.filter_by(library=library)
    return render_template('users.html', users=all_users)


@lbms_app.route('/add_user', methods=['GET', 'POST'])
@is_logged_in
def add_user():
    """View function to add user into database"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        library = Library.query.filter_by(email=session['email']).first()
        user = User(name=name, email=email, phone=phone, library=library)
        db.session.add(user)
        db.session.commit()
        flash("New user is added", "success")
        return redirect(url_for('users'))


@lbms_app.route('/update', methods=['GET', 'POST'])
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


@lbms_app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    """View function to remove entries from User table"""
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User Deleted Successfully")
    return redirect(url_for('users'))

@lbms_app.route('/books', methods=['GET', 'POST'])
@is_logged_in
def books():
    """View function for user management page"""
    library = Library.query.filter_by(email=session['email']).first()
    all_books = Book.query.filter_by(library=library)
    return render_template('books.html', books=all_books)

@lbms_app.route('/add_book', methods=['GET', 'POST'])
@is_logged_in
def add_book():
    """View function to add user into database"""
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        genre = request.form['genre']
        author = request.form['author']
        shelf = request.form['shelf']
        library = Library.query.filter_by(email=session['email']).first()
        book=Book(
            title=title,isbn=isbn,
            genre=genre,author=author,
            shelf=shelf,library=library)
        db.session.add(book)
        db.session.commit()
        flash("New book is added", "success")
        return redirect(url_for('books'))

@lbms_app.route('/update_book', methods=['GET', 'POST'])
@is_logged_in
def update_book():
    """View function for updating user info"""
    if request.method == 'POST':
        book = Book.query.get(request.form.get('id'))
        book.title = request.form['title']
        book.isbn = request.form['isbn']
        book.genre = request.form['genre']
        book.author = request.form['author']
        book.shelf = request.form['shelf']

        db.session.commit()
        flash("Book Information Updated Successfully")

        return redirect(url_for('books'))
