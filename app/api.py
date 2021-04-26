from flask import session, redirect, url_for, flash, request
from app import lbms_app, db, bcrypt
from app.models import Library, Book, Author, Member
from functools import wraps

def register_library(name, email, password):
    password = bcrypt.generate_password_hash(
        password).decode('utf-8')
    library = Library(
        name=name,
        email=email,
        password=password)
    db.session.add(library)
    db.session.commit()

def login_user(email):
    library = Library.query.filter_by(
        email=email).first()
    session['logged_in'] = True
    session['email'] = email
    session['library_id'] = library.library_id

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

def get_allbooks():
    library = Library.query.get(session['library_id'])
    all_books = Book.query.filter_by(library=library)
    return all_books

def search_books(search_by, search_string, all_books):
    
    if search_by == 'Title':        
        books = searchby_title(search_string, all_books)
    elif search_by == 'Author':
        books = searchby_author(search_string, all_books)
    return books

def searchby_title(title, all_books):
    books = all_books.filter(Book.title.like("%{}%".format(title)))
    page = 1
    books = books.order_by(
        Book.registered_date.desc()).paginate(
            page=page,per_page=lbms_app.config['PER_PAGE_COUNT'])
    return books

def searchby_author(author, all_books):
    authors = Author.query.filter(Author.name.like("%{}%".format(author))).all()
        
    books = authors[0].books
    for author in authors[1:]:
        books.append(author.books)
    page = 1
    books = books.order_by(
        Book.registered_date.desc()).paginate(
            page=page,
            per_page=lbms_app.config['PER_PAGE_COUNT'])
    return books

def get_members():
    library = Library.query.filter_by(email=session['email']).first()
    all_members = Member.query.filter_by(library=library)
    return all_members

def add_member_db(name, email, phone):
    library = Library.query.filter_by(email=session['email']).first()
    member = Member(name=name, email=email, phone=phone, library=library)
    db.session.add(member)
    db.session.commit()

def update_member_db(id, name, email, phone):
    member = Member.query.get(id)
    member.name = name
    member.email = email
    member.phone = phone

    db.session.commit()

def delete_member_db(id):
    member = Member.query.get(id)
    db.session.delete(member)
    db.session.commit()

def add_book_db(
        title, isbn, total, authors):
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

def updata_book_db(book_id, title, isbn, total, authors):
    book = Book.query.get(book_id)
    book.title = title
    book.isbn = isbn
    diff = book.total - int(total)
    book.total = total
    book.available = book.available + abs(diff)
    updated_authors = authors
    for i in range(len(book.authors)):
        book.authors[i].name = updated_authors[i]

    db.session.commit()

def delete_book_db(book_id):
    book = Book.query.get(book_id)
    if Transaction.query.filter_by(book_id=book_id).count() != 0:
        flash('Cannot Delete, Alread issued copies', 'danger')
    else:
        db.session.delete(book)
        db.session.commit()

def add_transaction(book_id, member_name):
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

def update_transaction(book_id, member_name):
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

def fetch_frappe(
        url, params, required):
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

def popular_books():
    books = Book.query.filter_by(
        library_id=session["library_id"])
    counts=[book.transactions.count() for book in books]
    counts = numpy.array(counts)
    index_1 = numpy.argsort(counts)[-10:]
    counts=counts[index_1].tolist()
    isbn = [books[i].isbn for i in index_1]
    available = [books[i].available for i in index_1]
    total = [books[i].total for i in index_1]
    return isbn, counts, total, required

def member_payments():
        members = Member.query.filter_by(
            library_id=session["library_id"])
        amount = [member.transactions.filter_by(if_returned=True).count() for member in members]
        amount = [lbms_app.config['RENT_FEE']*i for i in amount]
        amount = numpy.array(amount)
        index_2 = numpy.argsort(amount)[-10:]
        amount=amount[index_2].tolist()
        names = [members[i].name for i in index_2]
        return names, amount, index_2


