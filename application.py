import os
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import or_, and_
from wtforms_fields import *
from models import *

# Configure App

app = Flask(__name__)

app.secret_key = 'secret'

#configure database
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://lhqkptsjnyzkik:f8cf13cdc00796fd789d6f2cc514f88936d2620130eaeb7cecbcd3f10fd6f250@ec2-34-239-241-25.compute-1.amazonaws.com:5432/daitbrcvb621sd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#configure flask login

login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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
        user_object=User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        if current_user.is_authenticated:
            return "logged in with flask-login"
        return "not logged in :("
        #return redirect(url_for( 'search'))
    return render_template("login.html", form=login_form)

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == "GET":
        return render_template("search.html")
    else:
        isbn = request.form.get("isbn")
        title =  request.form.get("title")
        author =  request.form.get("author")

        books = Book.query.filter(or_ (Book.author.ilike(author), Book.isbn.ilike(isbn), Book.title.ilike(title)) ).all()

        #db.engine.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author",
                            #{"isbn": isbn, "title": title, "author": author}).fetchall()
        if len(books) == 0:
            return render_template("search.html")

        return render_template("result.html", books=books)


    #return "Hey! search for books..."

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return "User logged out!"

if __name__ == "__main__":

    app.run(debug=True)
