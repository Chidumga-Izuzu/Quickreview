from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from models import User


def invalid_credentials(form, field):
    """Username and password checker """

    username_entered = form.username.data
    password_entered = field.data

# check validity of username
    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("incorrect username or password")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("incorrect username or password")

class RegistrationForm(FlaskForm):

    """ Registration form """

    username = StringField('username_l', validators=[InputRequired(message="Please enter username"), Length(min=5, max=20, message= "Username must be between 5 and 20 characters")])
    password = PasswordField('password_l', validators=[InputRequired(message="password required"), Length(min=5, max=10, message= "Password must be between 5 and 10 characters")])
    confirm_password = PasswordField('confirm_password_l', validators=[InputRequired(message="Confirm password"), EqualTo('password', message="Passwords must match ")])
    submit_button = SubmitField ('Create Account')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")






class LoginForm(FlaskForm):

    """ Login form """

    username = StringField('username_l', validators=[InputRequired(message="Please enter a username")])
    password = PasswordField('password_l', validators=[InputRequired(message="password required"), invalid_credentials])

    submit_button = SubmitField ('Login')
