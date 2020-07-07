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

# CREATE TABLE `users` (
#   `id` INT NOT NULL AUTO_INCREMENT,
#   `username` VARCHAR(50) NOT NULL,
#   `password` VARCHAR(256) NOT NULL,
#   `money` INT NULL DEFAULT 1000.00,
#   PRIMARY KEY (`id`)
# )

# CREATE TABLE register (
# 	serial_no INT NOT NULL AUTO_INCREMENT,
#     user_id INT,
#     book_name VARCHAR(50) NOT NULL,
#     borrowed TIMESTAMP,
#     returned TIMESTAMP,
#     PRIMARY KEY (serial_no),
#     FOREIGN KEY (user_id) REFERENCES users(id)
#     );

