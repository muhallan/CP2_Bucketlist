import unittest
import json
from app import create_app, db


class BucketlistUpdateTestCase(unittest.TestCase):
    """This class represents the bucketlist updating test case"""

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

    def test_bucketlist_can_be_edited(self):
        """
        Test if a bucketlist can be retrieved, edited and saved
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Must visit the Grand Canyon!"
            })
        self.assertEqual(res.status_code, 200)

        # finally, we get the edited bucketlist to see if it is actually edited.
        results = self.client().get(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Must visit the', str(results.data))

    def test_bucketlist_edit_with_no_name_parameter(self):
        """
        Test what is displayed when a name is provided during bucketlist creation
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=dict())
        self.assertEqual(res.status_code, 400)
        self.assertIn('Parameter name missing.', str(res.data))

    def test_bucketlist_edit_with_empty_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with an empty name
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('Bucketlist name should not be empty.', str(res.data))

    def test_bucketlist_edit_with_duplicate_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with a name that already exists
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # then, we create a second bucketlist by making a POST request
        res2 = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'See the Mona Lisa'})
        self.assertEqual(res2.status_code, 201)
        # get the json with the bucketlist
        results2 = json.loads(res2.data.decode())

        # then, we edit the last created bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results2['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 409)
        self.assertIn('Bucketlist with this name already exists. Choose another name.', str(res.data))

    def test_single_bucketlist_edit_with_no_auth_header(self):
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
            data=self.bucketlist)

        # assert that the bucketlist is created
        self.assertEqual(res.status_code, 201)
        # get the response data in json format
        results = json.loads(res.data.decode())

        # edit a specific bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(),
            data={
                "name": "Must visit the Grand Canyon!"
            }
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_single_bucketlist_edit_with_invalid_token(self):
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

        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # edit a specific bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=access_token),
            data={
                "name": "Must visit the Grand Canyon!"
            }
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_single_bucketlist_edit_with_empty_token(self):
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

        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # edit a specific bucketlist by making a PUT request
        res = self.client().put(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=""),
            data={
                "name": "Must visit the Grand Canyon!"
            }
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))
