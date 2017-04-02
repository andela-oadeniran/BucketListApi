#!/usr/bin/env python
import unittest
# from datetime import datetime
from testcontext import get_item_or_raise_error


class TestUtilities(unittest.TestCase):
    '''
    Test suite for the helper functions
    used in the application
    '''
    def setUp(self):
        self.request_dict = {'name': 'fly a spaceship',
                             'created_by': 'ladi', 'items': []}

    def test_timestamp_function(self):
        # test time stamp is properly formated
        pass

    def test_get_item_or_400_name(self):
        # Test the utility method parses the argument
        result = get_item_or_raise_error(self.request_dict, 'name')
        self.assertEqual(result, 'fly a spaceship')

    def test_get_item_or_400_created_by(self):
        # test it returns for the key created_by,its value.
        result = get_item_or_raise_error(self.request_dict, 'created_by')
        self.assertEqual(result, 'ladi')

    def test_get_item_or_400_empty_items(self):
        # test for an empty item
        self.assertRaises(
            ValueError, get_item_or_raise_error, self.request_dict, 'items')

    if __name__ == '__main__':
        unittest.main()
