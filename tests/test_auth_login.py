import unittest
import json
from app import create_app, db


class AuthLoginTestCase(unittest.TestCase):
    """Test case for the login authentication."""

    def setUp(self):
        """
        Initialize and set up the test case
        :return:
        """
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_login(self):
        """
        Test if a user who is registered can login successfully
        :return:
        """
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # check if the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """
        Test if a user who is not registered cannot login
        :return:
        """
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login', data=not_a_user)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")

    def test_login_no_params(self):
        """
        Test if a correct message is returned when no parameter are supplied for the login
        :return:
        """
        # define an empty dictionary to represent empty params
        no_params = {}
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login', data=no_params)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'], "Email address and password not provided.")

    def test_login_no_email_param(self):
        """
        Test if a correct message is returned when no email parameter is supplied for the login
        :return:
        """
        # define a dictionary to represent empty email params
        no_email = {
            'password': 'nonepass'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login', data=no_email)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'], "Email address not provided.")

    def test_login_no_pass_param(self):
        """
        Test if a correct message is returned when no password parameter is supplied for the login
        :return:
        """
        # define a dictionary to represent empty password params
        no_email = {
            'email': 'email'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1/auth/login', data=no_email)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            result['message'], "Password not provided.")

    def test_login_empty_params(self):
        """
        Test if a correct message is returned when empty parameters are supplied for login
        :return:
        """
        # define a dictionary with empty params
        empty_data = {
            'email': '',
            'password': ''
        }
        res = self.client().post('/api/v1/auth/login', data=empty_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address and password is empty.")

    def test_login_empty_email(self):
        """
        Test if a correct message is returned when an empty email is supplied for registration
        :return:
        """
        # define a dictionary with empty email
        empty_email = {
            'email': '',
            'password': 'password'
        }
        res = self.client().post('/api/v1/auth/login', data=empty_email)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address is empty.")

    def test_login_empty_password(self):
        """
        Test if a correct message is returned when an empty password is supplied for registration
        :return:
        """
        # define a dictionary with empty password
        empty_password = {
            'email': 'email@company.com',
            'password': ''
        }
        res = self.client().post('/api/v1/auth/login', data=empty_password)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Password is empty.")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
            db.create_all()