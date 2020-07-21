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


user = {"id": None, "name": None}

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

        user.clear()

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
                mycursor.execute("SELECT password, user_id FROM users WHERE username = (%s)", (user_inp,)) 
                sql_ret = mycursor.fetchone()
                user["name"] = user_inp
        
        elif user_inp in emails:
                mycursor.execute("SELECT password, user_id, username FROM users WHERE email = (%s)", (user_inp,)) 
                sql_ret = mycursor.fetchone()
                user["name"] = sql_ret[2]


        if not check_password_hash(sql_ret[0], password):
                return apology("Incorrect Password")

        # Remember which user has logged in
        session["user_id"] = sql_ret[1]
        user["id"] = sql_ret[1]

        # Redirect user to home page
        return redirect('/homepage')
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Function for user registration
@app.route("/signUp", methods=["GET", "POST"])
def register():
        if request.method == "POST":

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
                user["id"] = u_id[0]

                # Creating an Entry for the user in the 'Books' table
                mycursor.execute(
                        "INSERT INTO books (user_id) VALUES (%s)", (user["id"],))
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
        for i in columns:
                mycursor.execute(f"SELECT user_id FROM books WHERE {i[0]} = 1")
                cur = mycursor.fetchall()
                if not cur:
                        continue
                for j in cur:
                        if user["id"] in j:
                                val = ' '.join(i[0].split('_'))
                                titles.append(val.title())

        mycursor.execute("SELECT name, money FROM users WHERE user_id = (%s)", (user["id"],))
        sql_ret = mycursor.fetchone()

        return render_template("homepage.html", books = titles, balance = sql_ret[1], name = sql_ret[0])


@app.route("/pages", methods=["GET", "POST"])
@login_required
def pages():
    # pages = convert_from_path('harry-potter-and-the-philosophers-stone-extract.pdf', 500)
    # i = 0
    # out = []
    # for page in pages:
    #     name = 'static/out' + str(i) + '.jpg'
    #     out.append(name)
    #     i += 1
    #     page.save(name, 'JPEG')
    # print(out)
    if request.method == "POST":
        selected = request.form["selected"]
        out = [selected]
        prefix = []
        for j in selected.split():
                prefix.append(j[0].lower())
        prefix = ''.join(prefix) + 'Out'
        for i in range(18):
                name = prefix + str(i)
                out.append(name)
        return render_template("pages.html", out = out)

@app.route("/explore")
def explore():
        mycursor.execute("SHOW columns FROM books")
        columns = mycursor.fetchall()
        titles = []
        for i in columns:
                val = ' '.join(i[0].split('_'))
                titles.append(val.title())
        titles.pop(0)
        return render_template("explore.html", books = titles)


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/')

@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow():
        selected = request.form["selected"]
        return render_template("borrow.html", book = selected)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
        selected = request.form["selected"]
        book = '_'.join(selected.lower().split())
        mycursor.execute(
                f"UPDATE books SET {book} = 1 WHERE user_id = (%s)", (user["id"],))
        mydb.commit()
        return redirect('/homepage')