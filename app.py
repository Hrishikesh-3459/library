import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from db_config import dbMysql

# Setup for database
db = dbMysql()
mydb = db.connection()
mycursor = mydb.cursor(buffered=True)
db.configure_db(mycursor)

user_id = None

# Function for user registration
def register():
    global user_id

    user = input("Enter username: ")
    password = input("Enter Password: ")

    # Generating a hash key for the user's password
    hash_pas = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    # Checking if the username already exists
    mycursor.execute(
            "SELECT * FROM users WHERE username = (%s)", (user,))
    rows = mycursor.fetchall()
    if rows and len(rows) != 0:
        print("Username exists")
        return 

    # Inserting username and password in the 'users' table
    mycursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)", (user, hash_pas))
    mydb.commit()

    # Retrieving the user_id
    mycursor.execute(
            "SELECT user_id FROM users WHERE username = (%s)", (user,))
    u_id = mycursor.fetchone()
    user_id = u_id[0]

    # Creating an Entry for the user in the 'Books' table
    mycursor.execute(
            "INSERT INTO books (user_id) VALUES (%s)", (user_id,))
    mydb.commit()

register()