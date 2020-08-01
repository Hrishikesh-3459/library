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
import time
import datetime

# Setup for database
db = dbMysql()
mydb = db.connection()
mycursor = mydb.cursor(buffered=True)
db.configure_db(mycursor)


# Just to show adithya how easy it is to upload files to github

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
        """ 
        Renders an apology page, whenever the user makes an error. 
        """

        return render_template("apology.html", bottom=message)

@app.route("/")
def index():
        """ 
        The main introductory page of the program. 
        """

        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Log user in
    """

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
        """ 
        Registers the user. 
        """

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
        """ 
        The homepage of the user logged in, showing the books they have along with their available balance 
        """

        mycursor.execute("SHOW columns FROM books")
        columns = mycursor.fetchall()

        # Keys in titles are the code, and the values are names
        titles = {}
        for i in columns:
                mycursor.execute(f"SELECT user_id FROM books WHERE {i[0]} = 1")
                cur = mycursor.fetchall()
                if not cur:
                        continue
                for j in cur:
                        if user["id"] in j:
                                val = (i[0].split('_'))
                                tmp = (''.join(list(zip(*val))[0]))
                                titles[tmp] = ' '.join(val).title()

        mycursor.execute("SELECT name, money FROM users WHERE user_id = (%s)", (user["id"],))
        sql_ret = mycursor.fetchone()

        if len(titles) == 0:
                return render_template("def_homepage.html", balance = sql_ret[1], name = sql_ret[0])

        return render_template("homepage.html", books = titles, balance = sql_ret[1], name = sql_ret[0])


@app.route("/pages", methods=["GET", "POST"])
@login_required
def pages():
    """ 
    Displaying the contents of the book. 
    """

    if request.method == "POST":
        selected = request.form["selected"]
        x = os.listdir("static")
        out = [selected+"Cover"]
        i = 1
        while True:
                name = selected + str(i)
                out.append(name)
                i += 1
                if (selected + str(i) + '.jpg') not in x:
                        break
        return render_template("pages.html", out = out, len = len(out))

@app.route("/explore")
def explore():
        """ 
        Shows the catalogue of the available books. 
        """

        mycursor.execute("SHOW columns FROM books")
        columns = mycursor.fetchall()

        # All of the available titles
        all_titles = list(columns)

        # The titles user already has
        user_titles = list()
        for i in columns:
                mycursor.execute(f"SELECT user_id FROM books WHERE {i[0]} = 1")
                cur = mycursor.fetchall()
                if not cur:
                        continue
                for j in cur:
                        if user["id"] in j:
                                user_titles.append(i)
        
        # Showing the titles that the user doesn't have
        for i in user_titles:
                all_titles.remove(i)
        
        # Keys in titles are the code, and the values are names
        titles = {}
        for i in all_titles:
                val = (i[0].split('_'))
                tmp = (''.join(list(zip(*val))[0]))
                titles[tmp] = ' '.join(val).title()
        fin = {}
        i = 0
        for j in titles:
                if i == 0:
                        i += 1
                        continue
                fin[j] = titles[j]

        # Create a list of books that the user has added to readlist
        
        mycursor.execute("SELECT book_name FROM readlist WHERE user_id = (%s)", (user["id"],))
        read_list_raw = list(mycursor.fetchall())

        read_list = []
        for i in read_list_raw:
                read_list.append(i[0])

        return render_template("explore.html", books = fin, read_list = read_list)


@app.route("/logout")
@login_required
def logout():
    """
    Log user out
    """

    # Forget any user_id
    global user
    session.clear()
    user = {"id": None, "name": None}

    # Redirect user to login form
    return redirect('/')

@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow():
        """ 
        Shows the user information about the payment and the book. 
        """

        selected = request.form["selected"].split()
        code = ''.join(list(zip(*selected))[0]).lower() 
        book = {"code": code, "name": ' '.join(selected)}
        return render_template("borrow.html", book = book)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
        """ 
        Records the user's purchase and adds the book to homepage. 
        """ 
        
        selected = request.form["selected"]
        book = '_'.join(selected.lower().split())

        # Get the current time
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        # Fetch the current balance of the user
        mycursor.execute("SELECT money FROM users WHERE user_id = (%s)", (user["id"],))
        money = mycursor.fetchone()
        balance = money[0] - 200

        # Checks if the user has enough balance
        if balance < 0:
                return apology("Not enough balance")


        # Update the books table to show that the current user has made the transaction
        mycursor.execute(
                f"UPDATE books SET {book} = 1 WHERE user_id = (%s)", (user["id"],))
        mydb.commit()

        # Update the register table and insert all the values into it
        mycursor.execute(f"INSERT INTO register (user_id, book_name, borrowed) VALUES (%s, %s, %s)", (user["id"], book, timestamp))
        mydb.commit()

        # Update the transactions table
        mycursor.execute(f"INSERT INTO transactions (user_id, book_name, borrowed) VALUES (%s, %s, %s)", (user["id"], book, timestamp))
        mydb.commit()

        # Update the users table
        mycursor.execute("UPDATE users SET money = (%s) WHERE user_id = (%s)", (balance, user["id"]))
        mydb.commit()

        return redirect('/homepage')

@app.route("/returnBook", methods=["GET", "POST"])
@login_required
def returnBook():
    """ 
    Displaying the contents of the book. 
    """
    selected = request.form["ret_selected"].split()
    code = ''.join(list(zip(*selected))[0]).lower() 
    book = {"code": code, "name": ' '.join(selected)}
    return render_template("returnBook.html", book = book)




@app.route("/about")
def contact():
        """ 
        Page where the contact info is displayed
        """

        return render_template("about.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
        """
        Records that the user has returned the book and reflects the info accordingly
        """

        if request.method == "POST":
                selected = request.form["selected"]
                book = '_'.join(selected.lower().split())
                
                # Get the current time
                ts = time.time()

                # raw time is in the format YYYY/MM/DD HH:MM:SS
                cur_time_raw = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                # Taking the borrowed time from database
                mycursor.execute(f"SELECT borrowed FROM library.register WHERE user_id = {user['id']} AND book_name = (%s)", (book,))
                borrowed_time_raw = mycursor.fetchall()
                
                # Formatted time is in the format YYYY/MM/DD in the form of string
                cur_time_formatted = (str(cur_time_raw)).split()[0]
                borrowed_time_formatted = (str(borrowed_time_raw[-1][-1])).split()[0]
                
                # Converting string form to list form
                cur_time_fin = list(map(int, cur_time_formatted.split('-')))   
                borrowed_time_fin = list(map(int, borrowed_time_formatted.split('-')))

                # Number of days between the two given dates
                d0 = datetime.date(cur_time_fin[0], cur_time_fin[1], cur_time_fin[2])
                d1 = datetime.date(borrowed_time_fin[0], borrowed_time_fin[1], borrowed_time_fin[2])
                delta = (d0 - d1).days

                mycursor.execute("SELECT money FROM users WHERE user_id = (%s)", (user["id"],))
                money = mycursor.fetchone()
                old_bal = money[0] + 200

                new_bal = old_bal - 10

                if delta > 7:
                        while delta != 7:
                                delta -= 1
                                new_bal -= 2

                fee = abs(new_bal - old_bal)
                # Database start

                # Update the books table to show that the current user has made the transaction
                mycursor.execute(
                        f"UPDATE books SET {book} = 0 WHERE user_id = (%s)", (user["id"],))
                mydb.commit()

                # Update the register table and insert all the values into it
                mycursor.execute(f"UPDATE register SET returned = (%s) WHERE user_id = (%s) AND borrowed = (%s) AND book_name = (%s)", (cur_time_raw, user["id"], borrowed_time_raw[-1][-1], book))
                mydb.commit()

                # Update the transactions table and insert all the values into it
                mycursor.execute(f"UPDATE transactions SET returned = (%s), fee = (%s) WHERE user_id = (%s) AND borrowed = (%s) AND book_name = (%s)", (cur_time_raw, fee, user["id"], borrowed_time_raw[-1][-1], book))
                mydb.commit()

                # Updating the user's balance
                mycursor.execute(
                        f"UPDATE users SET money = {new_bal} WHERE user_id = (%s)", (user["id"],))
                mydb.commit()

                return redirect('/homepage')


@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():

        ts = time.time()
        cur_time_raw = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time_formatted = (str(cur_time_raw)).split()[0]

        tran = []
        mycursor.execute("SELECT book_name, borrowed, returned FROM transactions WHERE user_id = (%s)", (user["id"],))
        data = mycursor.fetchall()
        for i,d in enumerate(data):
                val = [i+1]
                val.extend(d)
                tran.append(val)

        for i in tran:
                name_raw = i[1].split('_')
                name_fin = (' '.join(name_raw)).title()
                i[1] = name_fin # Formatting the name, removing the underscores and capitalising the first letter from each word

                borrowed_time_formatted = (str(i[2]).split())[0]

                # Converting string form to list form
                cur_time_fin = list(map(int, cur_time_formatted.split('-')))   
                borrowed_time_fin = list(map(int, borrowed_time_formatted.split('-')))

                if i[3] != None: # Checking if the user has already returned the book
                        cur_time_formatted = (str(i[3])).split()[0]
                        cur_time_fin = list(map(int, cur_time_formatted.split('-')))   
                        

                # Number of days between the two given dates
                d0 = datetime.date(cur_time_fin[0], cur_time_fin[1], cur_time_fin[2])
                d1 = datetime.date(borrowed_time_fin[0], borrowed_time_fin[1], borrowed_time_fin[2])
                delta = (d0 - d1).days

                mycursor.execute("SELECT money FROM users WHERE user_id = (%s)", (user["id"],))
                money = mycursor.fetchone()
                old_bal = money[0] + 200

                new_bal = old_bal - 10

                if delta > 7:
                        while delta != 7:
                                delta -= 1
                                new_bal -= 2

                # The fee that the user owes
                fee = abs(new_bal - old_bal)

                i.append(fee)

        if len(tran) == 0:
                return render_template("def_transactions.html")
        return render_template("transactions.html", transactions = tran)

@app.route("/readlist_add", methods=["GET", "POST"])
@login_required
def readlist_add():
        selected = request.form["read_selected"]

        add_remove(selected)

        return redirect('/explore')

@app.route("/readlist", methods=["GET", "POST"])
@login_required
def readlist():
        if request.method == "GET":
                mycursor.execute("SELECT book_name FROM readlist WHERE user_id = (%s)", (user["id"],))
                books_raw = list(mycursor.fetchall())

                titles = {}
                for i in books_raw:
                        val = (i[0].split())
                        tmp = (''.join(list(zip(*val))[0]))
                        titles[tmp.lower()] = ' '.join(val).title()

                return render_template("readlist.html", books = titles)
        else:
                selected = request.form["read_selected"]

                add_remove(selected)

                return redirect("/readlist")

def add_remove(selected):
        mycursor.execute("SELECT book_name FROM readlist WHERE user_id = (%s)", (user["id"],))
        books_raw = mycursor.fetchall()

        books = []
        for i in books_raw:
                books.append(i[0])
        
        if selected not in books:
                mycursor.execute("INSERT INTO readlist(book_name, user_id) VALUES (%s, %s)", (selected, user["id"]))
                mydb.commit()

        else:
                mycursor.execute("DELETE FROM readlist WHERE book_name = (%s) AND user_id = (%s)", (selected, user["id"]))
                mydb.commit()
