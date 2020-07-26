# Quickreview
Harvardx CS50W Project1


This web application is project 1 of HarvardX: CS50W Web Programming with Python and JavaScript.

It's a book review website that allows users to register, log in, search for books, leave reviews, and access reviews by other users. 

The application uses a third-party API by Goodreads, another book review website, to pull in ratings from a broader audience. Finally, users can also query for book details via the website's API. 

To run this app, you need to do the following: 

Create a virtual env for each application
	python -m venv project1
	 
	2) activate virtual environment -
	source env/bin/activate
	 
	 
	3) Install flask
	pip3 install flask
	pip3 install Flask-Session
	pip3 install werkzeug==0.16.0
	pip3 install Flask-SQLAlchemy
	pip3 install psycopg2
	pip3 install requests
	 	 
	4) set the application environment
	export FLASK_APP = application.py
	export FLASK_DEBUG = 1
	export FLASK_ENV=development

export DATABASE_URL=[insert url here]
	 
	5) Flask run
	 
	
