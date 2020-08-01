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
$ mkdir voiceControlledCalculator
$ cd voiceControlledCalculator
$ virtualenv venv --system-site-packages
$ source venv/bin/activate
(venv) $ pip3 install Flask
```
##### Windows

```
$ pip3 install virtualenv
$ mkdir voiceControlledCalculator
$ cd voiceControlledCalculator
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

## Built with

* [Python](https://www.python.org/) - Programming Language used

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The Web Framework used

* HTML - Markup Language used

* CSS - Style Sheet Language used

* [MySQL](https://www.mysql.com/) - Database Management System used.

## Authors

* [**Hrishikesh Mulkutkar**](https://github.com/Hrishikesh-3459)

* [**Adithya Neelakantan**](https://github.com/neelstrongarm)
