import os
import requests
from flask import Flask, session, request, logging, render_template, redirect, url_for
from flask import json, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import or_, and_
from sqlalchemy import join
from sqlalchemy.orm import scoped_session, sessionmaker
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


#Get book info
@app.route('/book/<isbn>', methods=["GET","POST"])
@login_required
def book(isbn):


    book = Book.query.get(isbn)
    if book is None:
        return render_template("error.html", message="Book not found"), 404

    if request.method == "POST":
        if "add" in request.form or "update" in request.form:
            comment = request.form.get("comment")
            rating = int(request.form.get("rating"))

            if (rating < 1 & rating > 5):
                return render_template("error.html", message="incorrect value")

            review_check = Review.query.filter(and_(Review.isbn==isbn, Review.username==current_user.username)).first()
            if review_check is None:
                review_add = Review(username=current_user.username, isbn=isbn, review=comment, review_numb=rating)
                db.session.add(review_add)

            else:
                review_check.review = comment
                review_check.review_numb = rating
            db.session.commit()

        elif "remove" in request.form:
            review_check = Review.query.filter(and_(Review.isbn==isbn, Review.username==current_user.username)).first()
            db.session.remove(review_check)
            db.session.commit()

    review_check = Review.query.filter(Review.isbn==isbn).all()
    user_review = [comment for comment in review_check if comment.username == current_user.username]
    if user_review:
        user_review=user_review[0]
        review_check.remove(user_review)
    # Get data from Goodreads API
    ### Change key to your goodreads API key below ###
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KGJIBaI7CKEgWvsELMOITA", "isbns": book.isbn})


    if res.status_code == 200:
        goodreads_Result = res.json()
        return render_template("results.html", book=book, goodreads_Result=goodreads_Result, review_check=review_check, user_review=user_review)
    return render_template("results.html", book=book, review_check=review_check, user_review=user_review)

@app.route("/api/<isbn>", methods=['GET', 'POST'])
@login_required
def api(isbn):

    book =Book.query.get(isbn)
    if book is None:
        return jsonify({"error": "Invalid Book ISBN"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "KGJIBaI7CKEgWvsELMOITA", "isbns": isbn})

    if res.status_code == 404:
        ratings_count = "Ratings Not Available"
        ratings_count = "Ratings Not Available"
    else:
        goodreads= res.json()
        for i in goodreads["books"]:
            ratings_count = i["ratings_count"]
            average_rating = i["average_rating"]

    return jsonify({


        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "ratings_count": ratings_count,
        "average_rating": average_rating
    })




@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == "__main__":

    app.run(debug=True)
