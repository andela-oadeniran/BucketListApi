#!/usr/bin/env python
import json
import unittest
from testcontext 


class BucketListTest(unittest.TestCase):
    '''
    The test suite for the bucket list resource
    POST : To create a new Bucket List
    GET : To retrieve the list of all Bucket Lists
    GET : Retrieve a single bucket list
    PUT: To update a single bucket list.
    DELETE: To remove a bucket List
    '''

    def setUp(self):
        # Set up the the test class.
        self.bucketlist = BucketListView()
        self.bucketlist1 = {'name': 'Do before 30', 'items': [],
        'created_by': }
        self.bucketlist_bad_input = {}

    def tearDown(self):
        # Called after the test class to clear data.
        del self.bucketlist
        del self.bucketlist1

    def test_invalid_json(self):
        # Should return valid for an invalid input
        pass

    def test_post_method_input(self):
        pass

    def test_post_method_successful(self):
        result = self.bucketlist.post(self.bucketlist1)
        expected = {'name': 'bucketlist1', 'items': [],
                    'created_by': 'ladi',
                    'date_modified': None}
        expected = json.dumps(expected), 201
        self.assertEqual(result, expected)


class BucketListsItemsTest(unittest.TestCase):
    '''
    The test suite for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''

    def setUp(self):
        # Set up the the test class.
        pass

    def tearDown(self):
        # Called after the test class to clear data.
        pass
