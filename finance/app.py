import os

import mysql.connector
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import time
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# "CREATE DATABASE IF NOT EXISTS finance"

# Configure CS50 Library to use SQLite database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="<<password>>",
    database="finance"
)
mycursor = db.cursor(buffered=True, dictionary=True)

# "CREATE TABLE 'users' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'username' TEXT NOT NULL, 'hash' TEXT NOT NULL, 'cash' NUMERIC NOT NULL DEFAULT 10000.00 )"
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, cash INT NOT NULL DEFAULT 10000.00 )")
db.commit()
mycursor.execute("CREATE TABLE IF NOT EXISTS transactions (user TEXT NOT NULL, symbol TEXT NOT NULL, shares INTEGER NOT NULL, price INTEGER NOT NULL, transacted TIMESTAMP NOT NULL)")
db.commit()
user = []
# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    mycursor.execute("SELECT user FROM transactions")
    check = mycursor.fetchall()
    if check:
        if (user[0] not in check[0]['user']):
            return render_template("def_index.html")

    mycursor.execute("SELECT * FROM transactions WHERE user = (%s)", (user[0],))
    inps = mycursor.fetchall()

    mycursor.execute("SELECT SUM(price * shares) AS total FROM transactions WHERE user = (%s)", (user[0],))
    total = mycursor.fetchall()
    if total[0]['total'] == None:
        total[0]['total'] = 0
    mycursor.execute("SELECT cash FROM users WHERE username = (%s)", (user[0],))
    cash = mycursor.fetchall()
    print(total)
    return render_template("index.html", inputs = inps, total = total, cash = cash[0]['cash'])


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # If either of the two entry fields are leftt empty
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("must provide symbol and shares", 403)

        # Number of shares the user has requested to buy
        shar = request.form.get("shares")
        if (shar.isdigit() == False):
            return apology("must provide positve integer", 403)
        # Symbol for the share the user wants to purchase
        symb = request.form.get("symbol")

        # Returned values from lookup
        retu = lookup(symb)
        if (retu == None):
            return apology("Invalid symbol", 403)
        cost = float(retu['price']) * float(shar)

        mycursor.execute("SELECT cash FROM users WHERE username = (%s)", (user[0],))
        cash = mycursor.fetchall()

        if (cost > cash[0]['cash']):
            return apology("Not enough cash", 403)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(
            ts).strftime('%Y-%m-%d %H:%M:%S')
        set_cash = cash[0]['cash'] - cost

        # mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL, cash NUMERIC NOT NULL DEFAULT 10000.00 )")
        # db.commit() 
        mycursor.execute("CREATE TABLE IF NOT EXISTS transactions (user TEXT NOT NULL, symbol TEXT NOT NULL, shares INTEGER NOT NULL, price INTEGER NOT NULL, transacted TIMESTAMP NOT NULL)")
        db.commit()
        mycursor.execute("INSERT INTO transactions (user, symbol, shares, price, transacted) VALUES (%s, %s, %s, %s, %s)",
                                                                                        (user[0], symb, shar, cost, timestamp))
        db.commit()
        mycursor.execute("UPDATE users SET cash = (%s) WHERE username = (%s)", (set_cash, user[0]))
        db.commit()
        return redirect("/")
    else:
        return render_template("buy.html")




@app.route("/history")
@login_required
def history():
    mycursor.execute("SELECT * FROM transactions WHERE user = (%s)", (user[0],))
    inps = mycursor.fetchall()
    return render_template("history.html", inputs = inps)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        mycursor.execute("SELECT * FROM users WHERE username = (%s)", (request.form.get("username"),))
        rows = mycursor.fetchall()
        # print(rows)
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form



@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        symb = request.form.get("symbol")
        retu = lookup(symb)
        if (retu == None):
            return apology("Invalid symbol", 403)
        return render_template("quoted.html", comp_name = retu['name'], sym = retu['symbol'], price = retu['price'])
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not request.form.get("confirmation"):
            return apology("must confirm password", 403)

        mycursor.execute("SELECT * FROM users WHERE username = (%s)", (request.form.get("username"),))
        rows = mycursor.fetchall()
        # Ensure username exists and password is correct
        if rows and len(rows) != 0:
            return apology("Username already exists", 403)
        pas = request.form.get("password")
        con = request.form.get("confirmation")

        if (pas != con):
            return apology("Passwords don't match", 403)

        if (len(pas) < 8):
            return apology("Password too short", 403)

        digCount = 0
        for i in pas:
            if (i.isdigit()):
                digCount += 1
        if (digCount < 1):
            return apology("Password must contain digits", 403)





        hash_pas = generate_password_hash(pas, method='pbkdf2:sha256', salt_length=8)
        user_name = request.form.get("username")
        mycursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (user_name, hash_pas))
        db.commit()
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        if not request.form.get("shares"):
            return apology("must provide number of shares", 403)


        sy = request.form.get("symbol")
        shar = request.form.get("shares")

        mycursor.execute("SELECT shares FROM transactions WHERE user = (%s) AND symbol = (%s)", (user[0], sy))
        avail_shares = mycursor.fetchall()

        if (int(shar) > int(avail_shares[0]['shares'])):
            return apology("given shares more than available shares", 403)

        symb = request.form.get("symbol")
        mycursor.execute("SELECT cash FROM users WHERE username = (%s)", (user[0],))
        cash = mycursor.fetchall()

        # Returned values from lookup
        retu = lookup(symb)
        cost = float(retu['price']) * float(shar)
        set_cash = cash[0]['cash'] + cost
        mycursor.execute("UPDATE users SET cash = %s WHERE username = %s", (set_cash, user[0]))
        db.commit()
        shar = int(shar) * (-1)
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(
            ts).strftime('%Y-%m-%d %H:%M:%S')
        mycursor.execute("INSERT INTO transactions (user, symbol, shares, price, transacted) VALUES (%s, %s, %s, %s, %s)",
                                                                                        (user[0], symb, shar, cost, timestamp))
        db.commit()
        return redirect("/")
    else:
        mycursor.execute("SELECT DISTINCT symbol FROM transactions WHERE user = (%s)", (user[0],))
        symbs = mycursor.fetchall()
        # print(symbs)
        return render_template("sell.html", symbo = symbs)




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
