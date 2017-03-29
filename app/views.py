#!/usr/bin/env python

from bucketlist import app
from flask import jsonify
from flask_restful import Resource, Api, reqparse, abort


class BucketLists(Resource):
    '''
    The class for the bucket list resource
    POST : To create a new Bucket List
    GET : To retrieve the list of all Bucket Lists
    GET : Retrieve a single bucket list
    PUT: To update a single bucket list.
    DELETE: To remove a bucket List
    '''

    def get(self):
        pass

    def post(self):
        # This handles the c`reation of a new bucketlist
        # logic
        pass

    def put(self):
        pass

    def delete(self):
        pass


class BucketListsItems(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''
    pass


class RegisterUser(Resource):
    pass


class LoginUser(Resource):
    pass


api = Api(app)
api.add_resource(BucketLists, "/bucketlists/")
if __name__ == '__main__':
    app.run(debug=True)
    