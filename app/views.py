#!/usr/bin/env python
import json
from bucketlist import app
from flask_restful import Resource, Api, reqparse, abort
from utilities import get_item_or_raise_error



class BucketListView(Resource):
    '''
    The class for the bucket list resource
    POST : To create a new Bucket List
    GET : To retrieve the list of all Bucket Lists
    GET : Retrieve a single bucket list
    PUT: To update a single bucket list.
    DELETE: To remove a bucket List
    '''

    def get(self):
        try:
            bucketlists = db.session.query.all()
        except:
            pass
        else:
            if bucketlists:
                return bucketlists, 201
            else:
                return 'Not found', 404

    def post(self, bucketlist):
        # This handles the c`reation of a new bucketlist
        # logic
        try:
            name = get_item_or_raise_error(bucketlist, 'name')
        except ValueError:
            return abort(400, message='ValueError')
        else:
            bucketlist = BucketList(name, created_by)
            return json.dumps(
                {
                    'id': bucketlist.id,
                    'name': bucketlist.name,
                    'items': bucketlist.items,
                    'date_created': bucketlist.date_created,
                    'date_modified': bucketlist.date_modified,
                    'created_by': 'ladi'
                })
      
    def put(self):
        pass

    def delete(self):
        pass


class BucketListItemView(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''
    pass


class RegisterUserView(Resource):
    pass


class LoginUserView(Resource):
    pass



api = Api(app)
api.add_resource(BucketListView, "/bucketlists/")
if __name__ == '__main__':
    app.run(debug=True)
    