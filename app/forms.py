from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from app import bcrypt
from app.models import Librarian
from email_validator import validate_email, EmailNotValidError


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
        librarian = Librarian.query.filter_by(name=name.data).first()
        if librarian:
            raise validators.ValidationError(
                'That name is taken. Please choose a different one.'
                )

    def validate_email(self, email):
        email = email.data
        try:
            # Validate.
            valid = validate_email(email)

            # Update with the normalized form.
            email = valid.email
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            raise validators.ValidationError(str(e))

        librarian = Librarian.query.filter_by(email=email).first()
        if librarian:
            raise validators.ValidationError(
                'That email is taken. Please choose a different one.'
                )


class LoginForm(FlaskForm):
    """This class defines the web form
    for the login page"""
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired()])

    def validate_email(self, email):
        email = email.data
        try:
            # Validate
            valid = validate_email(email)
            # Update with the normalized form.
            email = valid.email
        except EmailNotValidError as e:
            raise validators.ValidationError(str(e))
        # Search database for the entered email
        librarian = Librarian.query.filter_by(email=email).first()
        if not librarian:
            raise validators.ValidationError('Email not found')

    def validate_password(self, password):
        email = self.email.data
        librarian = Librarian.query.filter_by(email=email).first()
        if librarian:
            password_candidate = password.data
            if not bcrypt.check_password_hash(
                    librarian.password,
                    password_candidate):
                raise validators.ValidationError('Invalid Login')
