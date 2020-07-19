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

        user_inp = request.form.get("user_inp")
        password = request.form.get("password")

        # Query database for username
        mycursor.execute("SELECT username, email FROM users") 
        rows = mycursor.fetchall()
        names = []
        emails = []
        for i,j in rows:
                names.append(i)
                emails.append(j)

        # Ensure username exists and password is correct
        if user_inp not in names and user_inp not in emails:
                return apology("User not found")

        if user_inp in names:
                mycursor.execute("SELECT password FROM users WHERE username = (%s)", (user_inp,)) 
                password_in = mycursor.fetchone()
                # print(password_in[0])
        
        elif user_inp in emails:
                mycursor.execute("SELECT password FROM users WHERE email = (%s)", (user_inp,)) 
                password_in = mycursor.fetchone()
                # print(password_in)

        if not check_password_hash(password_in[0], password):
                return apology("Incorrect Password")
        # Remember which user has logged in
        session["user_id"] = user_inp
        user_name = request.form.get("username")
        user.clear()
        user.append(user_name)
        # Redirect user to home page
        return redirect('/homepage')
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

                # Checking if the email_id already exists
                mycursor.execute(
                        "SELECT * FROM users WHERE email = (%s)", (email,))
                rows = mycursor.fetchall()
                if rows and len(rows) != 0:
                        return apology("Email already exists")

                if password != confirmation:
                        return apology("Passwords don't match")

                # Generating a hash key for the user's password
                hash_pas = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

                # Inserting username and password in the 'users' table
                mycursor.execute(
                        "INSERT INTO users (username, password, email, name) VALUES (%s, %s, %s, %s)", (username, hash_pas, email, first_name))
                mydb.commit()

                # Retrieving the user_id
                mycursor.execute(
                        "SELECT user_id FROM users WHERE username = (%s)", (username,))
                u_id = mycursor.fetchone()
                user_id = u_id[0]

                # Creating an Entry for the user in the 'Books' table
                mycursor.execute(
                        "INSERT INTO books (user_id) VALUES (%s)", (user_id,))
                mydb.commit()

                return render_template("login.html")
        else:
                return render_template("signUp.html")

@app.route("/homepage")
@login_required
def homepage():
        mycursor.execute("SHOW columns FROM books")
        columns = mycursor.fetchall()
        titles = []
        lst = []
        for i in columns:
                mycursor.execute(f"SELECT user_id FROM books WHERE {i[0]} = 1")
                cur = mycursor.fetchall()
                lst = list(map(lst.append, cur))
                if user_id in lst:
                        val = ' '.join(i[0].split('_'))
                        titles.append(val.title())
        return render_template("homepage.html", books = titles)
# register()