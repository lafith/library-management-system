from flask import render_template, request, session
from flask import flash, redirect, url_for
from app import lbms_app, db, bcrypt
from app.models import Library, Member, Book, Author, Transaction
from app.forms import RegisterForm, LoginForm
from functools import wraps
from datetime import datetime

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
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        library = Library.query.filter_by(email=email).first()
        session['logged_in'] = True
        session['email'] = email
        session['library_id'] = library.library_id
        flash('You have been logged in!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


def is_logged_in(f):
    """This function will check if Member is logged in"""
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


@lbms_app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    """view function for dashboard page of each library"""
    if request.method == "POST":
        search_string = request.form["search"]
        search_by = request.form.get("searchby")
        if search_string != '':
            if search_by == 'Title':
                books = Book.query.filter_by(title=search_string, library_id=session['library_id']).all()
                return render_template('dashboard.html', books=books)
            elif search_by == 'Author':
                author = Author.query.filter_by(name = search_string).first()
                books = author.books
                return render_template('dashboard.html', books=books)
        else:
            library = Library.query.get(session['library_id'])
            all_books = Book.query.filter_by(library=library)
            return render_template('dashboard.html', books=all_books)
    else: 
        library = Library.query.get(session['library_id'])
        all_books = Book.query.filter_by(library=library)
        return render_template('dashboard.html', books=all_books)


@lbms_app.route('/members')
@is_logged_in
def members():
    """View function for Member management page"""
    library = Library.query.filter_by(email=session['email']).first()
    all_members = Member.query.filter_by(library=library)
    return render_template('members.html', members=all_members)


@lbms_app.route('/add_member', methods=['GET', 'POST'])
@is_logged_in
def add_member():
    """View function to add Member into database"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        library = Library.query.filter_by(email=session['email']).first()
        member = Member(name=name, email=email, phone=phone, library=library)
        db.session.add(member)
        db.session.commit()
        flash("New Member is added", "success")
        return redirect(url_for('members'))


@lbms_app.route('/update_member', methods=['GET', 'POST'])
@is_logged_in
def update_member():
    """View function for updating Member info"""
    if request.method == 'POST':
        member = Member.query.get(request.form.get('id'))
        member.name = request.form['name']
        member.email = request.form['email']
        member.phone = request.form['phone']

        db.session.commit()
        flash("Member Information Updated Successfully")

        return redirect(url_for('members'))


@lbms_app.route('/delete_member/<id>/', methods=['GET', 'POST'])
def delete_member(id):
    """View function to remove entries from Member table"""
    member = Member.query.get(id)
    db.session.delete(member)
    db.session.commit()
    flash("Member Deleted Successfully")
    return redirect(url_for('members'))


@lbms_app.route('/add_book', methods=['GET', 'POST'])
@is_logged_in
def add_book():
    """View function to add Member into database"""
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        total = request.form['total']
        authors = request.form.getlist("author[]")
        library = Library.query.filter_by(email=session['email']).first()
        book = Book(
            title=title, isbn=isbn,
            total=total, available=total,
            library=library)
        for name_ in authors:
            author = Author.query.filter_by(name=name_).first()
            if author:
                book.authors.append(author)
            else:
                author = Author(name=name_)
                db.session.add(author)
                book.authors.append(author)

        db.session.add(book)
        db.session.commit()

        flash("New book is added", "success")
        return redirect(url_for('dashboard'))


@lbms_app.route('/update_book', methods=['GET', 'POST'])
@is_logged_in
def update_book():
    """View function for updating Member info"""
    if request.method == 'POST':
        book = Book.query.get(request.form.get('id'))
        book.title = request.form['title']
        book.isbn = request.form['isbn']
        diff = book.total - int(request.form['total'])
        book.total = request.form['total']
        book.available = book.available + diff

        updated_authors = request.form.getlist('author[]')
        for i in range(len(book.authors)):
            book.authors[i].name = updated_authors[i]

        db.session.commit()
        flash("Book Information Updated Successfully")
        return redirect(url_for('dashboard'))


@lbms_app.route('/delete_book/<id>/', methods=['GET', 'POST'])
def delete_book(id):
    """View function to remove entries from Member table"""
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    flash("Book info Deleted Successfully")
    return redirect(url_for('dashboard'))

@lbms_app.route('/issue_book', methods=['GET', 'POST'])
@is_logged_in
def issue_book():
    """View function to issue a book"""
    if request.method == 'POST':
        member_name = request.form['member']
        book_id = request.form.get('book_id')
        book = Book.query.get(book_id)
        if book.available == 0:
            flash('No copies available to issue', 'danger')
        else:
            member = Member.query.filter_by(name = member_name).first()
            if member == None:
                flash('This member doesnt exist', 'danger')
            else:
                transactions = member.transactions
                return_column = transactions.with_entities(Transaction.if_returned)
                not_returned = return_column.filter_by(if_returned = False).count()
                debt = lbms_app.config['RENT_FEE'] * not_returned
                if debt <= lbms_app.config['DEBT_LIMIT']:
                    transaction = Transaction(
                        member_id = member.member_id,
                        book_id = book_id,
                        )
                    book.available = book.available - 1
                    db.session.add(transaction)
                    db.session.commit()
                    flash('Book issued successfully!','success')
                else:
                    flash('Debt has crossed the limit! Cannot issue more','danger')
        return redirect(url_for('dashboard'))