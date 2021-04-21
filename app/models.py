from app import db
from datetime import datetime

books_joint = db.Table(
    'books_joint',
    db.Column('library_id', db.Integer, db.ForeignKey('library.library_id')),
    db.Column('book_id', db.Integer, db.ForeignKey('book.book_id')),
    )


class Library(db.Model):
    """This class defines the table
    for library information
    """
    library_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='library', lazy=True)
    books = db.relationship(
        'Book', secondary=books_joint,
        backref=db.backref('libraries', lazy='dynamic'))

    def __repr__(self):
        return f"Library('{self.name}', '{self.email}')"


class User(db.Model):
    """This class defines the table
    for information of users/borrowers
    """
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'))

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Book(db.Model):
    """This class defines the table
    for storing info regarding books
    """
    book_id = db.Column(db.Integer, primary_key=True)
    tite = db.Column(db.String(20), nullable=False)
    isbn = db.Column(db.String(15), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Book('{self.title}', '{self.isbn}')"
