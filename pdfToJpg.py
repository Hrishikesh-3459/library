# Program to convert each page of the pdf file to a jpg
from pdf2image import convert_from_path

# Specify the path, and make sure that it is of the following format, i.e, it has the name of the book
path = "/Users/hrishikesh/codeBase/Flask/library/Harry Potter PDF/harry-potter-and-the-goblet-of-fire.pdf"

# Extracting the name from the path
name = path[path.rindex('/')+1:path.index('.pdf')].split('-')

# Creating a shortcut name
short_name = ''.join(list(zip(*name))[0])


# Converting
pages = convert_from_path(path, 500)
i = 1
for page in pages:
    name = f'static/{short_name}' + str(i) + '.jpg'
    i += 1
    page.save(name, 'JPEG')