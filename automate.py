# This file is used to convert PDS files to JPEG
# "pdf2image" is easy to install on mac -> brew install Poppler, then -> pip install pdf2image
# Make sure you have a database connected and ready.
# Try to stay accurate to the format specified for the path of the pdf file
# A new column in the "books" table will be automatically added
# You would also need to add a "cover" image for the book



from pdf2image import convert_from_path
from db_config import dbMysql
import mysql.connector

# Specify the path, and make sure that it is of the following format, i.e, it has the name of the book and each word is separated by a '-'.

path = "/Users/hrishikesh/codeBase/Flask/library/the-chronicles-of-narnia-the-lion-the-witch-and-the-wardrobe.pdf"

# Extracting the name from the path
full_name = path[path.rindex('/')+1:path.index('.pdf')].split('-')


# Creating a shortcut name
short_name = ''.join(list(zip(*full_name))[0])


# # Converting
pages = convert_from_path(path, 500)
i = 1
for page in pages:
    name = f'static/{short_name}' + str(i) + '.jpg'
    i += 1
    page.save(name, 'JPEG')

db = dbMysql()
mydb = db.connection()
mycursor = mydb.cursor(buffered=True)
db.configure_db(mycursor)

col_name = '_'.join(full_name)

mycursor.execute(f"ALTER TABLE books ADD {col_name} TINYINT(1) DEFAULT 0")
mydb.commit()