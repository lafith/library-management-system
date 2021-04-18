from app import db
from datetime import datetime


class Library(db.Model):
    """This class defines the database model
    for library information
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='library', lazy=True)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"Library('{self.name}', '{self.email}')"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.utcnow)
    library_id=db.Column(db.Integer, db.ForeignKey('library.id'))
        
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"