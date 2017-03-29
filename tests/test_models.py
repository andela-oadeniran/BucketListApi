# import modules
import unittest

from flask_sqlalchemy import SQLAlchemy
from testcontext import app, BucketList, BucketListItem, User
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/testbucketlist'
db = SQLAlchemy(app)


class TestUserModel(unittest.TestCase):
    '''
    The test suite for the Bucket list Api
    User model
    '''

    def setUp(self):
        # Create necessary connections fot the test suite.max_length
        self.user1 = User('ladi', 'ladi@')
        self.user2 = User('polymath', 'polymath@')

    def tearDown(self):
        # This takes down the data after running tests for the class
        del self.user1
        del self.user2

    def test_user_model(self):
        # Test to show that users are instances of the User Object
        self.assertIsInstance(self.user1, User)

    def test_user_name_data_integrity(self):
        # Test for data integrity
        self.assertNotEqual(self.user1.created_by, 'polymath')

    def test_user_name(self):
        # Test for valid attribute
        self.assertEqual(self.user2.created_by, 'polymath')

    def test_user_hash_password_integrity(self):
        # Test the user password
        self.assertNotEqual(self.user1.hash_password, 'polymath@')

    def test_valid_user_hash(self):
        # Test valid user hash password
        self.assertEqual(self.user2.hash_password, 'polymath@')


class TestBucketListModel(unittest.TestCase):
    '''
    Test suite for the Bucket list class Model.
    '''

    def setUp(self):
        # set up for the test suite
        self.bucketlist1 = BucketList('Things to do before I get married.')

    def tearDown(self):
        # tear down data for test suite after completion
        del self.bucketlist1

    def test_bucketlist_model(self):
        # test to show a bucketlist is an instance of the bucketlist class
        self.assertIsInstance(self.bucketlist1, BucketList)

    def test_bucket_list_name_integrity(self):
        # test bucket list item
        self.assertNotEqual(self.bucketlist1.bucket_list_name, 'Things to do')

    def test_valid_bucket_list_name(self):
        # test bucket list name
        self.assertEqual(
            self.bucketlist1.bucket_list_name,
            'Things to do before I get married.')


class TestBucketListItem(unittest.TestCase):
    '''
    Test Suite for the bucket list item class model.
    '''

    def setUp(self):
        # test suite set up method
        self.item1 = BucketListItem()

    def tearDown(self):
        # delete test suite data after use
        pass


if __name__ == '__main__':
    unittest.main()
