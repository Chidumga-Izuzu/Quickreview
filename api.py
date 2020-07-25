import os
import requests
from models import *

def main():

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KGJIBaI7CKEgWvsELMOITA", "isbns": book.isbn})







    if res.status_code == 404:
        ratings_countt = "No Ratings Available"
        average_rating = "No Ratings Available"
    else:
        goodreads_Result = res.json()
        for i in goodreads_Result["book"]:
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

if __name__ == "__main__":
    (main())
