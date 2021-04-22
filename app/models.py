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

    def __repr__(self):
        return f"Member('{self.name}', '{self.email}')"


class Book(db.Model):
    """This class defines the table
    for storing info regarding books
    """
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    isbn = db.Column(db.String(15), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    shelf = db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    available = db.Column(db.Integer, nullable=False)
    library_id = db.Column(db.Integer, db.ForeignKey('library.library_id'))
    def __repr__(self):
        return f"Book('{self.title}', '{self.isbn}')"
