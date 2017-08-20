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
            db.create_all()

    def test_bucketlist_creation(self):
        """
        Test if a bucketlist is actually created using a resulting status code
        :return:
        """
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_all_bucketlists(self):
        """
        Test if all the bucketlists can be retrieved
        :return:
        """
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/bucketlists/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Grand canyon', str(res.data))

    def test_api_can_get_bucketlist_by_id(self):
        """
        Test if a single bucketlist can be retrieved by its id
        :return:
        """
        res = self.client().post('/bucketlists/', data=self.bucketlist)
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/bucketlists/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Grand canyon', str(result.data))

    def test_bucketlist_can_be_edited(self):
        """
        Test if a bucketlist can be retrieved, edited and saved
        :return:
        """
        res = self.client().post(
            '/bucketlists/',
            data={'name': 'Visit the Grand canyon'})
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/bucketlists/1',
            data={
                "name": "Must visit the Grand Canyon!"
            })
        self.assertEqual(res.status_code, 200)
        results = self.client().get('/bucketlists/1')
        self.assertIn('Must visit the', str(results.data))

    def test_bucketlist_deletion(self):
        """
        Test if a bucketlist can be deleted
        :return:
        """
        res = self.client().post(
            '/bucketlists/',
            data={'name': 'Visit the Grand Canyon!'})
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/bucketlists/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/bucketlists/1')
        self.assertEqual(result.status_code, 404)