#!/usr/bin/env python

import unittest, sys
from testcontext import BucketList, BucketListItem


class BucketListsTest(unittest.TestCase):
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
        pass

    def tearDown(self):
        # Called after the test class to clear data.
        pass

    def test_invalid_json(self):
        # Should return valid for an invalid input
        pass


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
print(sys.path)