import os
import requests
from flask import Flask, session, request, logging, render_template, redirect, url_for
from flask import json, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import or_, and_
from sqlalchemy import join
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import sessionmaker
from wtforms_fields import *
from models import *

# Configure App

app = Flask(__name__)

app.secret_key = 'secret'

#configure database
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://lhqkptsjnyzkik:f8cf13cdc00796fd789d6f2cc514f88936d2620130eaeb7cecbcd3f10fd6f250@ec2-34-239-241-25.compute-1.amazonaws.com:5432/daitbrcvb621sd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


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
            return redirect(url_for('search'))
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
         if len(books) == 0:
            return render_template("search.html")

         return render_template("result.html", books=books)

#API for Book data
@app.route('/api/<isbn>', methods=["GET","POST"])
def vaidyalib_API(isbn):
    if request.method == "GET":
        search_results = Book.query.filter(Book.isbn == isbn).first()

        if search_results:
            books = {
                "title"          : search_results.title,
                "author"         : search_results.author,
                "year"          : search_results.year,
                "isbn"             : search_results.isbn,
                "review_count"  : search_results.review_count,
                "average_score" : str(search_results.average_rating)
            }

            response = jsonify(books)
            response.status_code = 200
            return response
        else:
            response = jsonify("404: Nothing Here")
            response.status_code = 404
            return response

    return render_template("search.html")


@app.route('/book/<isbn>', methods=["GET","POST"])
@login_required
def book(isbn):
    if request.method == "GET":


        reviewed = reviews.query.filter(reviews.isbn == isbn).all()

        for reviewed_by_current_user in reviewed:
            if (reviewed_by_current_user.username.strip() == current_user.username):
                session['user_has_reviewed'] = True

        goodreads_results = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KGJIBaI7CKEgWvsELMOITA", "isbns": isbn})

        search_results = Book.query.filter(Book.isbn == isbn).first()

        return render_template("results.html", book = search_results, goodreads_results = goodreads_results.json(), review=reviewed )
    return render_template("search.html")



@app.route('/rate_book', methods=["GET","POST"])
@login_required
def rate_book():
    rvalue = -1
    if request.method == "POST":

        session['user_has_rated'] = True

        rating = int(request.form['value'])

        current_rating = Book.query.filter_by(Book.isbn == isbn).first()

        if current_rating.ratings is not None:
            rate        = current_rating.ratings
            average_ratings = current_rating.average_rating
            average_ratings = ((average_ratings*ratings)+rating)/(rate+1)

            current_rating.average_rating      = average_ratings
            current_rating.ratings = rate+1
        else:
            current_rating.ratings = 1
            current_rating.average_rating    = rating
        db.session.commit()

        return redirect(url_for('book', isbn=session['current_book']))
    return url_for('book', isbn=session['current_book'])



@app.route('/review_book', methods=["GET","POST"])
@login_required
def review_book():

    if request.method == "POST":

        review = request.form['review']
        current_review = Book.query.filter_by(isbn = session['current_book']).first()

        if current_review.review_count is not None:
            current_review.review_count = current_review.review_count+1
            db.session.commit()
        else:
            current_review.review_count = 1
            db.session.commit()

        review_data = reviews(username = current_user.username, isbn = session['current_book'], review = review)
        db.session.add(review_data)
        db.session.commit()

        return redirect(url_for('book', isbn=session['current_book']))

    return url_for('book', isbn=session['current_book'])

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    return "User logged out!"

if __name__ == "__main__":

    app.run(debug=True)
