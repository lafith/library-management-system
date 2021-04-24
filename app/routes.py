from flask import render_template, request, session, Response
from flask import flash, redirect, url_for
from app import lbms_app, db, bcrypt
from app.models import Library, Member, Book, Author, Transaction
from app.forms import RegisterForm, LoginForm
from functools import wraps
from datetime import datetime
import requests
import math
import numpy
import io
import csv


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
                books = Book.query.filter_by(
                    title=search_string,
                    library_id=session['library_id'])
                books = books.order_by(
                    Book.registered_date.desc()).paginate(
                        page=page,per_page=lbms_app.config['PER_PAGE_COUNT'])
                
                return render_template('dashboard.html', books=books)
            elif search_by == 'Author':
                author = Author.query.filter_by(
                    name = search_string).first()
                books = author.books
                books = books.order_by(
                    Book.registered_date.desc()).paginate(
                        page=page,
                        per_page=lbms_app.config['PER_PAGE_COUNT'])
                return render_template('dashboard.html', books=books)
        else:
            library = Library.query.get(session['library_id'])
            all_books = Book.query.filter_by(library=library)
            all_books = all_books.order_by(
                Book.registered_date.desc()).paginate(
                    page=page,
                    per_page=lbms_app.config['PER_PAGE_COUNT'])
            return render_template('dashboard.html', books=all_books)
    else:
        library = Library.query.get(session['library_id'])
        page = request.args.get('page', 1, type=int)
        books_perpage = Book.query.filter_by(library=library)
        all_books = books_perpage.order_by(
            Book.registered_date.desc()).paginate(
                page=page,
                per_page=lbms_app.config['PER_PAGE_COUNT'])
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
        flash("Member Information Updated Successfully", "success")

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
        book.available = book.available + abs(diff)

        updated_authors = request.form.getlist('author[]')
        for i in range(len(book.authors)):
            book.authors[i].name = updated_authors[i]

        db.session.commit()
        flash("Book Information Updated Successfully", "success")
        return redirect(url_for('dashboard'))


@lbms_app.route('/delete_book/<id>/', methods=['GET', 'POST'])
def delete_book(id):
    """View function to remove entries from Member table"""
    book = Book.query.get(id)
    if Transaction.query.filter_by(book_id=id).count() != 0:
        flash('Cannot Delete, Alread issued copies', 'danger')
    else:
        db.session.delete(book)
        db.session.commit()
        flash("Book info Deleted Successfully", 'danger')
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

@lbms_app.route('/return_book', methods=['GET', 'POST'])
@is_logged_in
def return_book():
    """View function to return a book"""
    if request.method == 'POST':
        member_name = request.form['member']
        book_id = request.form.get('book_id')
        book = Book.query.get(book_id)
        member = Member.query.filter_by(name = member_name).first()
        if member == None:
            flash('This member doesnt exist', 'danger')
        else:
            if book.available == book.total:
                flash(' Error! available is same as total stock', 'danger')
            else:
                transaction = member.transactions.filter_by(
                    member_id=member.member_id,
                    book_id=book_id, if_returned=False).first()
                if transaction is not None:
                    print('hurrayyy')
                    transaction.if_returned = True
                    book.available = book.available + 1
                    db.session.commit()
                    flash('Return Confirmed', 'success')
                else:
                    flash('Not issued to this member', 'danger')
        return redirect(url_for('dashboard'))


@lbms_app.route('/import_books', methods=['GET', 'POST'])
@is_logged_in
def import_books():
    url="https://frappe.io/api/method/frappe-library"
    if request.method == 'POST':
        params=request.form.to_dict()
        required = int(params['total'])
        params.popitem()
        params = {key:val for key, val in params.items() if val != ''}
        total_page = math.ceil(required/20)
        
        data=[]
        for i in range(total_page):
            params['page'] = i+1
            msg = single_request(url,params)
            data.append(msg)
        data = [item for page in data for item in page]
        
        if len(data)>required:
            data = data[0:required]
            
        for book in data:
            title = book['title']
            print(title)
            isbn = book['isbn13']
            if Book.query.filter_by(library_id=session["library_id"], isbn=isbn).count() == 1:
                continue
            else:
                total = 1
                authors = book["authors"]
                library = Library.query.get(session['library_id'])
                book = Book(
                title=title, isbn=isbn,
                total=total, available=total,
                library=library)
                authors = authors.split('/')
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
        return redirect(url_for('dashboard'))

def single_request(url,params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except HTTPError as http_err:
        flash(f'HTTP error occurred: {http_err}', 'danger')
    except Exception as err:
        flash(f'Other error occurred: {err}', 'danger')
    else:
        print('Success!')
        data = response.json()
        return data['message']


@lbms_app.route('/download_report/<rp>')
@lbms_app.route('/report', methods=['GET', 'POST'])
@is_logged_in
def report(rp=None):

    books = Book.query.filter_by(
        library_id=session["library_id"])
    counts=[book.transactions.count() for book in books]
    counts = numpy.array(counts)
    index_1 = numpy.argsort(counts)[-10:]
    counts=counts[index_1].tolist()
    isbn = [books[i].isbn for i in index_1]
    available = [books[i].available for i in index_1]
    total = [books[i].total for i in index_1]

    
    members = Member.query.filter_by(
        library_id=session["library_id"])
    amount = [member.transactions.filter_by(if_returned=True).count() for member in members]
    amount = [lbms_app.config['RENT_FEE']*i for i in amount]
    amount = numpy.array(amount)
    index_2 = numpy.argsort(amount)[-10:]
    amount=amount[index_2].tolist()
    names = [members[i].name for i in index_2]

    if rp == '01':
        output = io.StringIO()
        writer = csv.writer(output)
        
        line = ['Title','ISBN','Total Transactions','Available','Total']
        writer.writerow(line)

        for i,j in enumerate(index_1):
            line = [
                books[j].title, books[j].isbn,
                counts[i], books[j].available,
                books[j].total]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output, mimetype="text/csv",
            headers={"Content-Disposition":"attachment;filename=book_report.csv"})
    elif rp == '02':
        output = io.StringIO()
        writer = csv.writer(output)
        
        line = ['Name','Amount']
        writer.writerow(line)

        for i,j in enumerate(index_2):
            line = [
                members[j].name,
                amount[i]
                ]
            writer.writerow(line)
        output.seek(0)
        return Response(
            output, mimetype="text/csv",
            headers={"Content-Disposition":"attachment;filename=payment_report.csv"})
    return render_template(
        'report.html', labels=isbn,
        data=counts, available=available,
        total=total, names=names, amount=amount)
