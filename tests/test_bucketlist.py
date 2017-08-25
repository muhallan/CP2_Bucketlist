import contextlib
import unittest
import os
import json
from app import create_app, db
from sqlalchemy import MetaData, engine

meta = MetaData()


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
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_bucketlist_creation_with_no_auth_header(self):
        """
        Test what message is displayed when no header is provided
        :return:
        """
        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_bucketlist_creation_with_invalid_token(self):
        """
        Test if a bucketlist is actually created using a resulting status code
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization=access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_bucketlist_creation_with_empty_token(self):
        """
        Test what message is displayed when a header is provided with an empty token
        :return:
        """
        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization=""),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))

    def test_bucketlist_creation_with_no_name_parameter(self):
        """
        Test what is displayed when a name is provided during bucketlist creation
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=dict())
        self.assertEqual(res.status_code, 400)
        self.assertIn('Parameter name missing.', str(res.data))

    def test_bucketlist_creation_with_empty_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with an empty name
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('Bucketlist name should not be empty.', str(res.data))

    def test_bucketlist_creation_with_duplicate_name(self):
        """
        Test what is displayed when attempting to creating a bucketlist with a name that already exists
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a bucketlist by making a POST request
        res = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        # create the same bucketlist
        res_again = self.client().post(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        self.assertEqual(res_again.status_code, 409)
        self.assertIn('Bucketlist with this name already exists. Edit it or choose another name.', str(res_again.data))

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
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_bucketlist_retrieval_with_no_auth_header(self):
        """
        Test what message is displayed when no header is provided
        :return:
        """
        # get bucketlists by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/',
            headers=dict(),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_bucketlist_retrieval_with_invalid_token(self):
        """
        Test if a bucketlist is actually created using a resulting status code
        :return:
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # get bucketlists by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/',
            headers=dict(Authorization=access_token),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_bucketlist_retrieval_with_empty_token(self):
        """
        Test what message is displayed when a header is provided with an empty token
        :return:
        """
        # get bucketlists by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/',
            headers=dict(Authorization=""),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))

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
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a
        # GET request while supplying a limit as a query parameter
        res = self.client().get(
            '/api/v1/bucketlists?limit=30',
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
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)
        self.assertEqual(res.status_code, 201)

        # get all the bucketlists that belong to the test user by making a
        # GET request while supplying a limit as a query parameter
        res = self.client().get(
            '/api/v1/bucketlists?q=canyon',
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
            '/api/v1/bucketlists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.bucketlist)

        # assert that the bucketlist is created
        self.assertEqual(res.status_code, 201)
        # get the response data in json format
        results = json.loads(res.data.decode())

        result = self.client().get(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the bucketlist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Grand canyon', str(result.data))

    def test_single_bucketlist_retrieval_with_no_auth_header(self):
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

        # get a specific bucketlist by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Header with key Authorization missing.', str(res.data))

    def test_single_bucketlist_retrieval_with_invalid_token(self):
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

        # get a specific bucketlist by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=access_token),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid token format.', str(res.data))

    def test_single_bucketlist_retrieval_with_empty_token(self):
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

        # get a specific bucketlist by making a GET request
        res = self.client().get(
            '/api/v1/bucketlists/{}'.format(results['id']),
            headers=dict(Authorization=""),)
        self.assertEqual(res.status_code, 401)
        self.assertIn('Token not provided in the header with key Authorization.', str(res.data))

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

    def test_update_bucketlist_item(self):
        """Test if a bucketlist item can be edited"""
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
        # get the json containing the created bucketlist item
        res_item = json.loads(res.data.decode())

        # then, we edit the created bucketlist by making a PUT request
        rv = self.client().put(
            '/api/v1/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Eat fried crabs mixed with honey"
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited bucketlist to see if it is actually edited.
        results = self.client().get(
            '/api/v1/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('mixed with honey', str(results.data))

    def test_delete_bucketlist_item(self):
        """Test if an item in a bucketlist can be deleted"""
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
        # get the json containing the created bucketlist item
        res_item = json.loads(res.data.decode())

        # delete the bucketlist item we just created
        res = self.client().delete(
            '/api/v1/bucketlists/{}/items/{}'.format(results['id'], res_item['id']),
            headers=dict(Authorization="Bearer " + access_token), )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/api/v1/bucketlists/{}/items/1'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
            db.create_all()

    if __name__ == "__main__":
        unittest.main()
