# CP2_Bucketlist
[![Codeship Status for muhallan/CP2_Bucketlist](https://app.codeship.com/projects/28fd47e0-6a1d-0135-313c-321e1b150d94/status?branch=master)](https://app.codeship.com/projects/241824)
[![Code Climate](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/gpa.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist)
[![Test Coverage](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/coverage.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist/coverage)
[![Issue Count](https://codeclimate.com/github/muhallan/CP2_Bucketlist/badges/issue_count.svg)](https://codeclimate.com/github/muhallan/CP2_Bucketlist)

CP2_Bucketlist is a Python Flask built REST API which is lets one create, record and keep track of a list of items that they want to do before they die.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Pre-requisites
* Python versions 2.7, 3.3 to 3.7

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
$ mkvirtualenv CP2_Bucketlist
```

Install dependencies

```
$ pip install -r requirements.txt
```

Run the API

```
$ python run.py
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

