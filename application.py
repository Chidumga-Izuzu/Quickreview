from flask import Flask, render_template
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

            #Add user to database
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return "Registered!"


    return render_template("index.html", form=reg_form)


if __name__ == "__main__":
    app.run(debug=True)
