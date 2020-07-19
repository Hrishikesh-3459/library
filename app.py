# app.py for library
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from db_config import dbMysql
import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import datetime
import time
from functools import wraps

# Setup for database
db = dbMysql()
mydb = db.connection()
mycursor = mydb.cursor(buffered=True)
db.configure_db(mycursor)

user_id = None
user_name = None
user = []

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def apology(message):
        return render_template("apology.html", bottom=message)

@app.route("/")
def index():
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        mycursor.execute("SELECT * FROM users WHERE username = (%s)", (request.form.get("username"),))
        rows = mycursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        user_name = request.form.get("username")
        user.clear()
        user.append(user_name)
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Function for user registration
@app.route("/signUp", methods=["GET", "POST"])
def register():
        if request.method == "POST":
                global user_id
                global user_name

                first_name = request.form.get("first_name")
                email = request.form.get("email")
                username = request.form.get("username")
                password = request.form.get("password")
                confirmation = request.form.get("confirmation")
                
                # Checking if the username already exists
                mycursor.execute(
                        "SELECT * FROM users WHERE username = (%s)", (username,))
                rows = mycursor.fetchall()
                if rows and len(rows) != 0:
                        return apology("Username already exists")

                if password != confirmation:
                        return apology("Passwords don't match")

                # Generating a hash key for the user's password
                hash_pas = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

                # Inserting username and password in the 'users' table
                mycursor.execute(
                        "INSERT INTO users (username, password, email, name) VALUES (%s, %s)", (username, hash_pas, email, first_name))
                mydb.commit()

                # Retrieving the user_id
                mycursor.execute(
                        "SELECT user_id, FROM users WHERE username = (%s)", (user,))
                u_id = mycursor.fetchone()
                user_id = u_id[0]

                # Creating an Entry for the user in the 'Books' table
                mycursor.execute(
                        "INSERT INTO books (user_id) VALUES (%s)", (user_id,))
                mydb.commit()
        else:
                return render_template("signUp.html")

@app.route("/books")
def books():
        return render_template("books.html")
# register()