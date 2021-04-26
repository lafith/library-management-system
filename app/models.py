from app import db
from datetime import datetime


class Library(db.Model):
    """This class defines the table
    for library information
    """
    library_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('Member', backref='library', lazy=True)
    books = db.relationship('Book', backref='library', lazy=True)

    def __repr__(self):
        return f"Library('{self.name}', '{self.email}')"


class Member(db.Model):
    """This class defines the table
    for information of memebers/borrowers
    """
    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'))
    transactions = db.relationship(
        'Transaction', backref='member', lazy='dynamic')

    def __repr__(self):
        return f"Member('{self.name}', '{self.email}')"


# Association table for books and authors:
authorship = db.Table(
    'authorship',
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.author_id'))
)


class Book(db.Model):
    """This class defines the table
    for storing info regarding books
    """
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    isbn = db.Column(db.String(15), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer, nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    authors = db.relationship(
        'Author', secondary=authorship,
        backref=db.backref('books', lazy='dynamic'))
    library_id = db.Column(
        db.Integer, db.ForeignKey('library.library_id'))
    transactions = db.relationship(
        'Transaction', backref='book', lazy='dynamic')

    def __repr__(self):
        return f"Book('{self.title}', '{self.isbn}')"


class Author(db.Model):
    """This class defines the table
    for storing author info
    """
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)


class Transaction(db.Model):
    """This class defines the table
    for storing transactions detail
    """
    transaction_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.member_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    if_returned = db.Column(db.Boolean, default=False)
