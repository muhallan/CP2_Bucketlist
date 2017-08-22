import unittest
import os
import json
from app import create_app, db


class BucketlistTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

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

    def test_bucketlist_creation(self):
        """
        Test if a bucketlist is actually created using a resulting status code
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """
        Test if all the bucketlists can be retrieved
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a GET request
        res = self.client().get(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_all_bucketlists_with_pagination(self):
        """
        Test if all the bucketlists can be retrieved when a limit query parameter is provided
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a
        # GET request while supplying a limit as a query parameter
        res = self.client().get(
            '/bucketlists?limit=30',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_all_bucketlists_with_search_query(self):
        """
        Test if all the bucketlists can be retrieved when a search query parameter is provided
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a
        # GET request while supplying a limit as a query parameter
        res = self.client().get(
            '/bucketlists?q=canyon',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """
        Test if a single bucketlist can be retrieved by its id
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        # assert that the bucketlist is created
        self.assertEqual(res.status_code, 201)
        # get the response data in json format
        results = json.loads(res.data.decode())

        result = self.client().get(
            '/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Grand canyon', str(result.data))

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
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        res = self.client().put(
            '/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Must visit the Grand Canyon!"
            })
        self.assertEqual(res.status_code, 200)

        # finally, we get the edited bucketlist to see if it is actually edited.
        results = self.client().get(
            '/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Must visit the', str(results.data))

    def test_bucketlist_deletion(self):
        """
        Test if a bucketlist can be deleted
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Visit the Grand Canyon!'})
        self.assertEqual(res.status_code, 201)
        # get the bucketlist in json
        results = json.loads(res.data.decode())

        # delete the bucketlist we just created
        res = self.client().delete(
            '/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token), )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/bucketlists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_create_new_bucketlist_item(self):
        """Test if a new item can be added to an existing bucketlist"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # create a bucketlist item by making a POST request and add it to the created bucketlist
        res = self.client().post(
            '/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs"
            })
        self.assertEqual(res.status_code, 201)
        self.assertIn('Eat fried', str(res.data))

    def test_update_bucketlist_item(self):
        """Test if a bucketlist item can be edited"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # create a bucketlist item by making a POST request and add it to the created bucketlist
        res = self.client().post(
            '/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs"
            })
        self.assertEqual(res.status_code, 201)
        # get the json containing the created bucketlist item
        res_item = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        rv = self.client().put(
            '/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs mixed with honey"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited bucketlist to see if it is actually edited.
        # TODO requires implementing a GET for this too
        results = self.client().get(
            '/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('mixed with honey', str(results.data))

    def test_delete_bucketlist_item(self):
        """Test if an item in a bucketlist can be deleted"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        # get the json with the bucketlist
        results = json.loads(res.data.decode())

        # create a bucketlist item by making a POST request and add it to the created bucketlist
        res = self.client().post(
            '/bucketlists/{}/items/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs"
            })
        self.assertEqual(res.status_code, 201)
        # get the json containing the created bucketlist item
        res_item = json.loads(res.data.decode())

        # delete the bucketlist item we just created
        res = self.client().delete(
            '/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token), )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        # TODO requires implementing a GET for this too
        result = self.client().get(
            '/bucketlists/{}/items/1'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    if __name__ == "__main__":
        unittest.main()
