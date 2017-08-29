import unittest
import json
from app import create_app, db


class BucketlistDeletionTestCase(unittest.TestCase):
    """This class represents the bucketlist deletion test case"""

    def setUp(self):
        """
        Initialize the app and its test client and our test database
        :return:
        """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.bucketlist = {'name': 'Go to Grand canyon for camping'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """
        Helper method to help register a test user
        :param email:
        :param password:
        :return:
        """
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/api/v1/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """
        Helper method to help login a test user
        :param email:
        :param password:
        :return:
        """
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('api/v1/auth/login', data=user_data)

    def test_bucketlist_deletion(self):
        """
        Test if a bucketlist can be deleted
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand Canyon!'})
        self.assertEqual(res.status_code, 201)
        # get the bucketlist in json
        results = json.loads(res.data.decode())

        # delete the bucketlist we just created
        res = self.client().delete(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/api/v1/bucketlists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_single_bucketlist_delete_with_no_auth_header(self):
        """
        Test what message is displayed when no header is provided
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand Canyon!'})
        self.assertEqual(res.status_code, 201)
        # get the bucketlist in json
        results = json.loads(res.data.decode())

        # delete the bucketlist we just created
        res = self.client().delete(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(), )

        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_single_bucketlist_delete_with_invalid_token(self):
        """
        Test if a bucketlist is actually created using a resulting status code
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        # assert that the bucketlist is created
        self.assertEqual(res.status_code, 201)
        # get the response data in json format
        results = json.loads(res.data.decode())

        # edit a specific bucketlist by making a PUT request
        res = self.client().delete(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=access_token),
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_single_bucketlist_delete_with_empty_token(self):
        """
        Test what message is displayed when a header is provided with an empty token
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        # assert that the bucketlist is created
        self.assertEqual(res.status_code, 201)
        # get the response data in json format
        results = json.loads(res.data.decode())

        # edit a specific bucketlist by making a PUT request
        res = self.client().delete(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=""),
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))
