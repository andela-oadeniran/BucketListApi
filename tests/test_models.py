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
        self.assertNotEqual()


class TestBucketListModel(unittest.TestCase):
    '''
    Test suite for the Bucket list class Model.
    '''

    def setUp(self):
        # set up for the test suite
        self.bucketlist = BucketList('Things to do before getting married')

    def test_bucketlist_model(self):
        # test to show a bucketlist is an instance of the bucketlist class
        self.assertIsInstance(self.bucketlist, BucketList)


if __name__ == '__main__':
    unittest.main()
