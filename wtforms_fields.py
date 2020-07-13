from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    """ Registration Form """


    username = StringField('username_l', validators=[InputRequired(message="Please enter username"), Length(min=5, max=20, message= "Username must be between 5 and 20 characters")])
    password = PasswordField('password_l', validators=[InputRequired(message="password required"), Length(min=5, max=10, message= "Password must be between 5 and 10 characters")])
    confirm_password = PasswordField('confirm_password_l', validators=[InputRequired(message="Confirm password"), EqualTo('password', message="Passwords must match ")])
    submit_button = SubmitField ('Create Account')
