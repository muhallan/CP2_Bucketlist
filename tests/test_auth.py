import unittest
import json
from app import create_app, db


class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

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

    def test_registration(self):
        """
        Method to test if user registration works correctly
        :return:
        """
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a success message and a 201 status code
        self.assertEqual(result['message'], "You registered successfully. Please log in.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """
        Test to see if a user who is already existing can be registered again
        :return:
        """
        res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/api/v1/auth/register', data=self.user_data)
        self.assertEqual(second_res.status_code, 409)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_missing_register_params(self):
        """
        Test if a correct message is returned when no parameters are supplied for registration
        :return:
        """
        # define an empty dictionary to represent no data supplied
        no_data = {}
        res = self.client().post('/api/v1/auth/register', data=no_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address and password not provided.")

    def test_missing_register_email_param(self):
        """
        Test if a correct message is returned when no email parameter is supplied for registration
        :return:
        """
        # define a dictionary with missing email key
        password_data = {
            'password': 'password'
        }
        res = self.client().post('/api/v1/auth/register', data=password_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address not provided.")

    def test_missing_register_password_param(self):
        """
        Test if a correct message is returned when no password parameter is supplied for registration
        :return:
        """
        # define a dictionary with missing password key
        email_data = {
            'email': 'email'
        }
        res = self.client().post('/api/v1/auth/register', data=email_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Password not provided.")

    def test_register_empty_params(self):
        """
        Test if a correct message is returned when empty parameters are supplied for registration
        :return:
        """
        # define a dictionary with empty params
        empty_data = {
            'email': '',
            'password': ''
        }
        res = self.client().post('/api/v1/auth/register', data=empty_data)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address and password is empty.")

    def test_register_empty_email(self):
        """
        Test if a correct message is returned when an empty email is supplied for registration
        :return:
        """
        # define a dictionary with empty email
        empty_email = {
            'email': '',
            'password': 'password'
        }
        res = self.client().post('/api/v1/auth/register', data=empty_email)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Email address is empty.")

    def test_register_empty_password(self):
        """
        Test if a correct message is returned when an empty password is supplied for registration
        :return:
        """
        # define a dictionary with empty password
        empty_password = {
            'email': 'email@company.com',
            'password': ''
        }
        res = self.client().post('/api/v1/auth/register', data=empty_password)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Password is empty.")

    def test_register_invalid_email(self):
        """
        Test if a correct message is returned when an invalid email is supplied for registration
        :return:
        """
        # define a dictionary with an invalid email key
        fake_email = {
            'email': 'email',
            'password': 'password'
        }
        res = self.client().post('/api/v1/auth/register', data=fake_email)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Invalid email address.")

    def test_register_short_password(self):
        """
        Test if a correct message is returned when a short password is supplied for registration
        :return:
        """
        # define a dictionary with short passsword
        fake_email = {
            'email': 'email@company.co',
            'password': 'pass'
        }
        res = self.client().post('/api/v1/auth/register', data=fake_email)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Password too short.")

    def test_register_short_password_and_invalid_email(self):
        """
        Test if a correct message is returned when a short password and an invalid email are supplied for registration
        :return:
        """
        # define a dictionary with an invalid email and short password
        fake_email = {
            'email': 'email',
            'password': 'pass'
        }
        res = self.client().post('/api/v1/auth/register', data=fake_email)
        self.assertEqual(res.status_code, 400)
        result = json.loads(res.data.decode())
        self.assertEqual(
            result['message'], "Invalid email address and short password.")

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
    # TODO test what happens when not all credentials are not given
    # TODO email validation
