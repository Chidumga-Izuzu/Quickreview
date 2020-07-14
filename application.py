from flask import Flask, render_template, redirect, url_for
from passlib.hash import pbkdf2_sha256

from wtforms_fields import *
from models import *

# Configure App

app = Flask(__name__)

app.secret_key = 'replace later'

#configure database
app.config['SQLALCHEMY_DATABASE_URI']='postgres://lhqkptsjnyzkik:f8cf13cdc00796fd789d6f2cc514f88936d2620130eaeb7cecbcd3f10fd6f250@ec2-34-239-241-25.compute-1.amazonaws.com:5432/daitbrcvb621sd'

db = SQLAlchemy(app)

@app.route("/", methods=['GET', 'POST'])
def index():

    reg_form = RegistrationForm()

    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        #hash password

        hashed_pass = pbkdf2_sha256.hash(password)

            #Add user to database
        user = User(username=username, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    #Allow login if validation is successful

    if login_form.validate_on_submit():
        return "logged in!"

    return render_template("login.html", form=login_form)




if __name__ == "__main__":
    app.run(debug=True)
