from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.id

class Book(db.Model):
    """ books model """

    __tablename__ = "books"
    isbn = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    year = db.Column(db.Integer, nullable=False)

# Returns information about the book in JSON format
    def toJson(self):
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "isbn": self.isbn,
            "review_count": self.getReviewsnumb(),
            "average_score": self.getReviewsAvg(),
        }

    def getReviewsnumb(self):
        return len(Review.query.filter_by(isbn=self.isbn).all())

    # Get average review rating for the book (returns 0.0 if no reviews)
    def getReviewsAvg(self):
        reviewer = Review.query.filter_by(isbn=self.book_id).with_entities(Review.review_numb).all()
        reviewer = [r for r, in reviewer]
        if reviewer:
            return sum(reviewer) / len(reviewer)
        else:
            return 0.0


class Review(db.Model):
    """ reviews model """

    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), db.ForeignKey('users.username'), nullable=False)
    isbn = db.Column(db.String(), db.ForeignKey('books.isbn'), nullable=False)
    review = db.Column(db.String(), nullable=False)
    review_numb = db.Column(db.SmallInteger, unique=False, nullable=False)


    def getUsername(self):
        return User.query.filter_by(id=self.id).first().username
