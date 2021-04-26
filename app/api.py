from flask import session, redirect, url_for, flash
from app import lbms_app, db, bcrypt
from app.models import Library, Book, Author
from app.models import Member, Transaction
from functools import wraps
import math
import requests


def register_library(name, email, password):
    """Add new library account info into Register table

    Parameters
    ----------
    name : str
        name of library
    email : str
        unique email used by a library
    password : str
    """
    password = bcrypt.generate_password_hash(
        password).decode('utf-8')
    library = Library(
        name=name,
        email=email,
        password=password)
    db.session.add(library)
    db.session.commit()


def login_user(email):
    """Update session parameters on authentication

    Parameters
    ----------
    email : str
        Library email used for logging in
    """
    library = Library.query.filter_by(
        email=email).first()
    session['logged_in'] = True
    session['email'] = email
    session['library_id'] = library.library_id


def is_logged_in(f):
    """Check if user is logged in"""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


def get_allbooks():
    """Fetch all book info belonging to the library

    Returns
    -------
    BaseQuery
        Iterable object containing info of all books
    """
    library = Library.query.get(session['library_id'])
    all_books = Book.query.filter_by(library=library)
    return all_books


def search_books(search_by, search_string, all_books):
    """[summary]

    Parameters
    ----------
    search_by : str
        'Title' or 'Author'
    search_string : str
        Keyword for searching tables
    all_books : BaseQuery
        Info of all books

    Returns
    -------
    BaseQuery
        Info of books after filtering
    """
    if search_by == 'Title':
        books = searchby_title(search_string, all_books)
    elif search_by == 'Author':
        books = searchby_author(search_string, all_books)
    return books


def searchby_title(title, all_books):
    """Search Book table, but only Title column

    Parameters
    ----------
    title : str
        Keyword for searching
    all_books : BaseQuery
        Info of books after filtering

    Returns
    -------
    BaseQuery
        Info of books with title containing [title]
    """
    books = all_books.filter(Book.title.like("%{}%".format(title)))
    page = 1
    books = books.order_by(
        Book.registered_date.desc()).paginate(
            page=page, per_page=lbms_app.config['PER_PAGE_COUNT'])
    return books


def searchby_author(author, all_books):
    """Search Book table, but by specific author

    Parameters
    ----------
    author : str
        Keyword for searching
    all_books : BaseQuery
        Info of books after filtering

    Returns
    -------
    BaseQuery
        Info of books written by author whose name contains [author]
    """
    authors = Author.query.filter(
        Author.name.like(
            "%{}%".format(author))).all()
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
    """Fetch all member information

    Returns
    -------
    BaseQuery
        Iterable object containing all member info
    """
    library = Library.query.filter_by(email=session['email']).first()
    all_members = Member.query.filter_by(library=library)
    return all_members


def add_member_db(name, email, phone):
    """Add new entry to Member table

    Parameters
    ----------
    name : str
        name of the new member
    email : str
        email of the new member
    phone : str
        Contact number of the new member
    """
    library = Library.query.filter_by(email=session['email']).first()
    member = Member(name=name, email=email, phone=phone, library=library)
    db.session.add(member)
    db.session.commit()


def update_member_db(id, name, email, phone):
    """Update a given entry of member table

    Parameters
    ----------
    id : str
        Id of the member to be updated
    name : str
        Updated name of the member
    email : str
        Updated email of the member
    phone : str
        Updated Contact no. of the member
    """
    member = Member.query.get(id)
    member.name = name
    member.email = email
    member.phone = phone

    db.session.commit()


def delete_member_db(id):
    """Delete a given entry from Member table

    Parameters
    ----------
    id : str
        Id of the member to be removed
    """
    member = Member.query.get(id)
    db.session.delete(member)
    db.session.commit()


def add_book_db(
        title, isbn, total, authors):
    """Add new entry to Book table

    Parameters
    ----------
    title : str
        Title of the new book
    isbn : str
        ISBN of the new book
    total : str
        Total number of copies
    authors : list
        Names of authors
    """
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
    """Update a book entry

    Parameters
    ----------
    book_id : str
        Id of book to be updated
    title : str
        Updated title of the book
    isbn : str
        Updated ISBN of the book
    total : str
        Updated number of copies stored
    authors : list
        Updated list of names of authors
    """
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
    """Remove a book entry

    Parameters
    ----------
    book_id : str
        Id of the entry to be removed from the Book table
    """
    book = Book.query.get(book_id)
    if Transaction.query.filter_by(book_id=book_id).count() != 0:
        flash('Cannot Delete, Alread issued copies', 'danger')
    else:
        db.session.delete(book)
        db.session.commit()


def add_transaction(book_id, member_name):
    """Add a new entry into Transaction table on issuing a book

    Parameters
    ----------
    book_id : str
        Id of book to be issued in Book table
    member_name : str
        Name of the member to whom book is getting issued
    """
    book = Book.query.get(book_id)
    if book.available == 0:
        flash('No copies available to issue', 'danger')
    else:
        member = Member.query.filter_by(name=member_name).first()
        if member is None:
            flash('This member doesnt exist', 'danger')
        else:
            transactions = member.transactions
            return_column = transactions.with_entities(Transaction.if_returned)
            not_returned = return_column.filter_by(if_returned=False).count()
            debt = lbms_app.config['RENT_FEE'] * not_returned
            if debt <= lbms_app.config['DEBT_LIMIT']:
                transaction = Transaction(
                    member_id=member.member_id,
                    book_id=book_id,
                    )
                book.available = book.available - 1
                db.session.add(transaction)
                db.session.commit()
                flash('Book issued successfully!', 'success')
            else:
                flash(
                    'Debt has crossed the limit! Cannot issue more',
                    'danger')


def update_transaction(book_id, member_name):
    """Update Transaction entry on returning a book

    Parameters
    ----------
    book_id : str
        Id of book getting returned
    member_name : str
        Name of the member who issued the book
    """
    book = Book.query.get(book_id)
    member = Member.query.filter_by(name=member_name).first()
    if member is None:
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
    """Interface to fetch book info from Frappe API

    Parameters
    ----------
    url : str
        url of the frappe api
    params : dict
        Dictionary containing info like
        title and author
    required : int
        Number of entries to be imported
    """
    total_page = math.ceil(required/20)
    data = []
    for i in range(total_page):
        params['page'] = i+1
        msg = single_request(url, params)
        data.append(msg)
    data = [item for page in data for item in page]

    if len(data) > required:
        data = data[0:required]

    for book in data:
        title = book['title']
        isbn = book['isbn13']

        count = Book.query.filter_by(
            library_id=session["library_id"],
            isbn=isbn).count()

        if count == 1:
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


def single_request(url, params):
    """Get request for fetching 20 books

    Parameters
    ----------
    url : str
        url of Frappe API
    params : dict
        Dictionary containing info like
        title and author

    Returns
    -------
    list
        list of dictionaries with book information
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as err:
        flash(f'Error occurred: {err}', 'danger')
    else:
        print('Success!')
        data = response.json()
        return data['message']
