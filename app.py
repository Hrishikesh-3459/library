import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from db_config import dbMysql

db = dbMysql()
mydb = db.connection()
mycursor = mydb.cursor(buffered=True)
db.configure_db(mycursor)

user = input("Enter username: ")
password = input("Enter Password: ")
hash_pas = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)


mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, hash_pas))
mydb.commit()

