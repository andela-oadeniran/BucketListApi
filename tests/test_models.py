# # import modules
# from flask_testing import TestCase

# from testcontext import BucketList, BucketListItem, User


# class TestUserModel(TestCase):
#     '''
#     The test suite for the Bucket list Api
#     User model
#     '''

#     def setUp(self):
#         # Create necessary connections fot the test suite.max_length
#         self.user1 = User('ladi', 'ladi@')

#     def tearDown(self):
#         # This takes down the data after running tests for the class
#         del self.user1

#     def test_user_model(self):
#         # Test to show that users are instances of the User Object
#         self.assertIsInstance(self.user1, User)

#     def test_user_name(self):
#         # Test for valid attribute
#         self.assertEqual(self.user1.name, 'ladi')

#     def test_valid_user_hash(self):
#         # Test valid user hash password
#         self.assertEqual(self.user1.hash_password, 'ladi@')


# class TestBucketListModel(TestCase):
#     '''
#     Test suite for the Bucket list class Model.
#     '''

#     def setUp(self):
#         # set up for the test suite
#         self.bucketlist1 = BucketList('Things to do before I get married.',
#                                       'Sage')

#     def tearDown(self):
#         # tear down data for test suite after completion
#         del self.bucketlist1

#     def test_bucketlist_model(self):
#         # test to show a bucketlist is an instance of the bucketlist class
#         self.assertIsInstance(self.bucketlist1, BucketList)

#     def test_valid_bucket_list_name(self):
#         # test bucket list name
#         self.assertEqual(
#             self.bucketlist1.bucket_list_name,
#             'Things to do before I get married.')

#     def test_valid_created_by(self):
#         # created by the user
#         self.assertEqual(self.bucketlist1.created_by, 'Sage')

#     def test_date_created(self):
#         # when bucket list was initially created
#         self.assertTrue(self.bucketlist1.date_created)

#     def test_date_modified(self):
#         # defaults to date created
#         self.assertEqual(self.bucketlist1.date_modified, None)


# class TestBucketListItem(TestCase):
#     '''
#     Test Suite for the bucket list item class model.
#     '''

#     def setUp(self):
#         # test suite set up method
#         self.item1 = BucketListItem('Travel to Naples and florence',
#                                     '2017-03-29 05:40:26')
#         self.item2 = BucketListItem('Build a House', '2017-04-01 03:40:26',
#                                     done=True)

#     def tearDown(self):
#         # delete test suite data after use
#         del self.item1
#         del self.item2

#     def test_bucket_list_item(self):
#         # test the object is ann instance of the bucket list item.
#         self.assertIsInstance(self.item1, BucketListItem)

#     def test_bucket_list_item_name(self):
#         # test item name
#         self.assertEqual(self.item1.bucket_list_item_name,
#                          'Travel to Naples and florence')

#     def test_bucket_list_status_false(self):
#         # defaults to false
#         self.assertFalse(self.item1.done)

#     def test_bucket_list_status_true(self):
#         # test
#         self.assertEqual(self.item2.done, True)

#     def test_date_created(self):
#         # test date created
#         self.assertTrue(self.item2.date_created)

#     def test_date_modified(self):
#         # test date modified
#         self.assertEqual(self.item2.date_modified, '2017-04-01 03:40:26')


# if __name__ == '__main__':
#     unittest.main()
