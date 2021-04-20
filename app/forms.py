from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from app.models import Library


class RegisterForm(FlaskForm):
    """This class defines the web form
    for the registration page"""
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    def validate_name(self, name):
        library = Library.query.filter_by(name=name.data).first()
        if library:
            raise validators.ValidationError(
                'That name is taken. Please choose a different one.'
                )

    def validate_email(self, email):
        library = Library.query.filter_by(email=email.data).first()
        if library:
            raise validators.ValidationError(
                'That email is taken. Please choose a different one.'
                )


class BookForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    isbn = StringField('ISBN', [validators.Length(min=1, max=20)])
