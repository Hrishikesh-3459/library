import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Ramukaka",
    database="library"
)

mycursor = mydb.cursor(buffered=True)

user = "<<username>>"
password = "<<password>>"
hash_pas = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
print(hash_pas)

mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, hash_pas))
mydb.commit()