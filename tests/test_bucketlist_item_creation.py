import unittest
import json
from app import create_app, db


class BucketlistItemCreationTestCase(unittest.TestCase):
    """This class represents the bucketlist item creation test case"""

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

    def test_create_new_bucketlist_item(self):
        """Test if a new item can be added to an existing bucketlist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # create a bucketlist item by making a POST request and add it to the created bucketlist
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs"
            })
        self.assertEqual(res.status_code, 201)
        self.assertIn('Eat fried', str(res.data))

    def test_create_bucketlist_item_with_no_auth_header(self):
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

        # add a new bucketlist item
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(), data={
                "name": "Eat fried crabs"
            })

        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_create_bucketlist_item_with_invalid_token(self):
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

        # add a new bucketlist item
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization=access_token), data={
                "name": "Eat fried crabs"
            })

        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_create_bucketlist_item_with_empty_token(self):
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

        # add a new bucketlist item
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization=""), data={
                "name": "Eat fried crabs"
            }
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))

    def test_bucketlist_item_creation_with_no_name_parameter(self):
        """
        Test what is displayed when a name is provided during bucketlist creation
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

        # create a bucketlist item by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=dict())
        self.assertEqual(res.status_code, 400)
        self.assertIn('Parameter name missing.', str(res.data))

    def test_bucketlist_item_creation_with_empty_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with an empty name
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

        # create a bucketlist item by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('Bucketlist item name should not be empty.', str(res.data))

    def test_bucketlist_item_creation_with_duplicate_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with a name that already exists
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

        # create a bucketlist item by making a POST request
        self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'sky dive'})

        # create the same bucketlist
        res_again = self.client().post(
            '/api/v1/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'sky dive'})

        self.assertEqual(res_again.status_code, 409)
        self.assertIn('Bucketlist item with this name already exists in this bucketlist.'
                      ' Choose another name.', str(res_again.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
            db.create_all()

    if __name__ == "__main__":
        unittest.main()
