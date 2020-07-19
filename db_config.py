import mysql.connector


class dbMysql():
    def __init__(self):
        self.pwd = "Ramukaka"
        self.username = "root"
        self.host = "localhost"
        self.database = "library"
        self.mydb = None

    def connection(self):
        self.mydb = mysql.connector.connect(
            host=self.host,
            user=self.username,
            passwd=self.pwd,
            database=self.database
        )
        return(self.mydb)

    def configure_db(self, mycursor):
        mycursor.execute("CREATE DATABASE IF NOT EXISTS library")
        self.mydb.commit()
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INT NOT NULL AUTO_INCREMENT, username VARCHAR(255) NOT NULL, password VARCHAR(256) NOT NULL, money INT NULL DEFAULT 1000.00, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL,PRIMARY KEY (user_id))")
        self.mydb.commit()
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS register (serial_no INT NOT NULL AUTO_INCREMENT, user_id int, book_name VARCHAR(50) NOT NULL, borrowed TIMESTAMP, returned TIMESTAMP, PRIMARY KEY (serial_no), FOREIGN KEY (user_id) REFERENCES users(user_id))")
        self.mydb.commit()
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS books (user_id int, philosophers_stone TINYINT(1) DEFAULT 0, chamber_of_secrets TINYINT(1) DEFAULT 0, prisoner_of_azkaban TINYINT(1) DEFAULT 0, goblet_of_fire TINYINT(1) DEFAULT 0, order_of_the_phoenix TINYINT(1) DEFAULT 0, half_blood_prince TINYINT(1) DEFAULT 0, deathly_hallows TINYINT(1) DEFAULT 0, FOREIGN KEY (user_id) REFERENCES users(user_id))")
        self.mydb.commit()


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

