#!/usr/bin/env python
import json
from bucketlist import app, db
from flask import request
from flask_restful import Resource, Api, reqparse, abort
# from app.utilities import get_item_or_raise_error
from models import BucketList, BucketListItem, User


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
        ret_json = []
        bucketlists = BucketList.query.all()
        if bucketlists:
            for bucketlist in bucketlists:
                ret_json.append(self.return_bucket_list_attributes(bucketlist))
            return json.dumps(ret_json)
        return abort(404)

    def post(self):
        # This handles the c`reation of a new bucketlist
        # logic
        # return {'request': request.args.get('name')}
        name = request.args.get('name')
        if not name:
            abort(400)
        else:
            bucketlist = BucketList(name, 'ladi')
            db.session.add(bucketlist)
            db.session.commit()
            return json.dumps(
                self.return_bucket_list_attributes(bucketlist))

    @staticmethod
    def return_bucket_list_attributes(bucketlist):
        # parse the attributes of a bucketlist object and return
        return {
            'id': bucketlist.id,
            'name': bucketlist.name,
            'items': bucketlist.items,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.created_by
        }


class BucketListIdView(Resource):
    '''
    This handles the bucket list id
    endpoint.
    '''

    def get(self, bucketlist_id):
        # for the get request returns a bucketlist
        # with the id specified in the url
        try:
            bucketlist = BucketList.query.get(bucketlist_id)
            return {
                'id': bucketlist.id,
                'name': bucketlist.name,
                # 'items': bucketlist.items
            }
        except AttributeError:
            return abort(404, msg='Not found')

    def put(self, bucketlist_id):
        # view to update a single bucket list
        # modified date changes
        try:
            name = request.args.get('name')
            if name:
                db.session.query(BucketList).filter(
                    BucketList.id == bucketlist_id).update(
                    {'name': name})
                db.session.commit()
            else:
                raise ValueError
        except IndexError:
            pass
        except ValueError:
            pass

    def delete(self, bucketlist_id):
        # view to delete a bucket list with the associated id
        try:
            db.session.query(
                BucketList).filter(BucketList.id == bucketlist_id).delete()
            db.commit()
        except IndexError:
            pass

    # @staticmethod


class BucketListItemView(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''

    def post(self):
        # method to handle post request
        pass

    def put(self):
        # method handles the put request to the resource
        pass

    def delete(self):
        # method handles the delete request to the route
        pass


class RegisterUserView(Resource):
    pass


class LoginUserView(Resource):
    pass



    



api = Api(app)
api.add_resource(BucketListView, "/bucketlists/")
api.add_resource(BucketListIdView, "/bucketlists/<int:bucketlist_id>")
if __name__ == '__main__':
    app.run(debug=True)

BucketListView().get()
    