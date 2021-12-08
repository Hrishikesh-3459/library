# Library

Web based library application.

## Getting Started

Please make sure to do all of this before you run the code

### Prerequisites

* Python

* Flask

* werkzeug

* Flask-Session

* mysql-connector-python

* Local MySQL Database

### Installing

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the packages.

#### Installing Flask

##### Mac

Type all of this in the terminal

```
$ pip3 install virtualen
$ mkdir library
$ cd library
$ virtualenv venv --system-site-packages
$ source venv/bin/activate
(venv) $ pip3 install Flask
```
##### Windows

```
$ pip3 install virtualenv
$ mkdir library
$ cd library
$ py -3 -m venv venv
$ venv\Scripts\activate
(venv) $ pip3 install flask
```

#### Installing Werkzeug

```
pip install Werkzeug
```

#### Installing Flask-Sessions

```
pip install Flask-Session
```

#### Installing MySQL Connector

```
pip install mysql-connector-python
```

#### Installing MySQL

Download [MySQL](https://dev.mysql.com/downloads/mysql/) and go through the setup process, and make sure to keep note of your host, username and password.

After installing MySQL, go to **db_config.py** and enter your host, username and password in the "init" function.

**Note:** You will have to create a database named 'library'

```
CREATE DATABASE library;
```

## Running

##### Mac

Type all of this in the terminal

```
$ export FLASK_APP=app.py
$ flask run
```

##### Windows

```
$ flask run
````

Visit http://127.0.0.1:5000 to see the app running

## Screenshots

### Index 

![index](https://user-images.githubusercontent.com/51927760/89092981-fb8b6c00-d3d3-11ea-8e05-8dbb737bf5bf.png)

### Sign Up

![Sign Up](https://user-images.githubusercontent.com/51927760/89093041-70f73c80-d3d4-11ea-9531-3b3f27c7e8cf.png)

### Explore 

![Explore](https://user-images.githubusercontent.com/51927760/89092962-d139ae80-d3d3-11ea-8963-3246cb6ee7b8.png)

### Borrow

![Screenshot 2020-08-01 at 08 55 17](https://user-images.githubusercontent.com/51927760/89093084-c4698a80-d3d4-11ea-8f63-fafdb2d39450.png)

### Homepage

![Homepage](https://user-images.githubusercontent.com/51927760/89092967-e0b8f780-d3d3-11ea-88e9-2245400a0ba2.png)

## Built with

* [Python](https://www.python.org/) - Programming Language used

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The Web Framework used

* [MySQL](https://www.mysql.com/) - Database Management System used.

* [JavaScript](https://www.javascript.com/) - Programming Language used (Front-End)

* HTML - Markup Language used

* CSS - Style Sheet Language used

## Authors

* [**Hrishikesh Mulkutkar**](https://github.com/Hrishikesh-3459)

* [**Adithya Neelakantan**](https://github.com/neelstrongarm)
