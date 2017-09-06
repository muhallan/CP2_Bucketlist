# CP2_Bucketlist
[![Codeship Status for muhallan/CP2_Bucketlist](https://app.codeship.com/projects/28fd47e0-6a1d-0135-313c-321e1b150d94/status?branch=master)](https://app.codeship.com/projects/241824)
[![Code Climate](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/gpa.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist)
[![Test Coverage](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/coverage.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist/coverage)
[![Issue Count](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/issue_count.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist)

CP2_Bucketlist is a Python Flask built REST API which is lets one create, record and keep track of a list of items that they want to do before they die.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. A linux machine is assumed.

### Pre-requisites
* [Python](https://docs.python.org/3/) versions 2.7, 3.3 to 3.7
* [Git](https://git-scm.com/)
* [pip](https://pypi.python.org/pypi/pip)
* [PostgreSQL](https://www.postgresql.org/docs/current/static/tutorial.html)
* [virtualenv](https://virtualenv.pypa.io/en/stable/)

Ensure you have installed PostgreSQL in your computer and it's server is running locally on port 5432


### API Features
* Register and Sign up to the API
* Create various bucketlists. A bucketlist contains bucketlist items
* Fetch, update and delete bucketlists
* Add bucketlist items to bucketlists
* Read, update and delete bucketlist items
* Token-based authentication


### Installing

Clone the repo

```
$ git clone https://github.com/muhallan/CP2_Bucketlist.git
$ cd CP2_Bucketlist
```

Create the virtualenv

```
$ pip install virtualenv
$ virtualenv venv
```

Export environment variables. This as well starts the virtual environment venv

```
$ source .env
```
Install dependencies in the virtual environment

```
$ pip install -r requirements.txt
```

Create Postgres databases for use in testing and development

```
$ createdb test_db
$ createdb bucketlist_api_dev
```
Set up the databases by running migrations
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```
Run the API

```
$ python manage.py runserver
```

To access the API on the server, and interface with it, fire up Postman and run this url
http://localhost:5000/api/v1/login, select POST, and in the body, put parameters with keys *email* and *password*

### Running the tests

```
$ python manage.py test
```


### Viewing the test coverage

```
$ python manage.py cov
```

## Author

**Muhwezi Allan**

