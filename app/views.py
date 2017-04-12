#!/usr/bin/env python
from collections import OrderedDict
from bucketlist import app, db
from flask import request, g, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, abort, reqparse
from utilities import save
from models import BucketList, BucketListItem, User
from sqlalchemy import and_

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        username_or_token = username_or_token.title()
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


class BucketListAPI(Resource):
    '''
    The class for the bucket list resource
    POST : To create a new Bucket List
    GET : To retrieve the list of all Bucket Lists
    GET : Retrieve a single bucket list
    PUT: To update a single bucket list.
    DELETE: To remove a bucket List
    '''
    decorators = [auth.login_required]

    def __init__(self, reqparse=reqparse):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True, type=str)

    def post(self, g=g, db=db, bucketlist_id=None):
        # This handles the creation of a new bucketlist
        if bucketlist_id:
            abort(404, message="Invalid URL")
        self.name = self.parser.parse_args().get('name')
        created_by = g.user.username
        if not self.name.strip():
            abort(400, message='Bucket list name cannot be empty!')
        elif BucketList.query.filter_by(
                created_by=created_by).filter_by(name=self.name).first():
            abort(400, message='Bucket List name already exists')
        else:
            bucketlist = BucketList(self.name, created_by)
            if save(bucketlist, db):
                return bucketlist.as_dict(), 201  # return serialize
            return abort(400, message='Error in request!!!')

    def get(self, bucketlist_id=None, g=g):
        # get the list of bucket lists or an item and return.
        created_by = g.user.username
        if bucketlist_id:
            bucketlist = BucketList.query.filter_by(
                created_by=created_by).filter_by(id=bucketlist_id).first()
            return bucketlist.as_dict()
        else:
            bucketlists = BucketList.query.filter_by(
                created_by=created_by).all()
            if bucketlists:
                return OrderedDict(
                    [('Bucketlist{}'.format(
                        bucketlist.id), bucketlist.as_dict())
                        for bucketlist in bucketlists])
            return abort(404, message='You don\'t have any bucketlist yet!')

    def put(self, bucketlist_id=None, g=g, db=db):
        # update a bucketlist with id(bucketList_id)
        if not bucketlist_id:
            abort(404, message="Invalid URL")
        self.name = self.parser.parse_args().get('name')
        created_by = g.user.username
        if not self.name.strip():
            abort(400, message="Name field cannot be empty")
        else:
            if db.session.query(
                BucketList).filter(and_(
                    BucketList.created_by == created_by,
                    BucketList.id == bucketlist_id)).update(
                    {'name': self.name}):
                db.session.commit()
                return BucketList.query.get(bucketlist_id).as_dict()
            return abort(404, message='Bucketlist{} does not exist'.format(
                bucketlist_id))

    def delete(self, bucketlist_id=None, g=g, db=db):
        # view to delete a bucket list with the associated id
        if not bucketlist_id:
            abort(404, message="Invalid URL")
        created_by = g.user.username
        if db.session.query(BucketList).filter(
            and_(
                BucketList.created_by == created_by,
                BucketList.id == bucketlist_id)).delete():
            db.session.commit()
        else:
            abort(
                404, message='Bucketlist{} does not exist'.format(
                    bucketlist_id))


class BucketListItemView(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''
    decorators = [auth.login_required]

    def post(self):
        # method to handle post request
        item_name = request.json.get('name')
        if item_name:
            item = BucketListItem(item_name)
        else:
            abort(400)
        bucketlist = BucketList.query.get_or_404(bucketlist_id)
        db.session.add(item)
        db.session.commit()
        return {
               "items": bucketlist.items       
          }

    def put(self, bucketlist_id, item_id):
        # method handles the put request to the resource
        # name = request.args.get('name')
        done = request.json.get('done')
        if done.title() == "True":
            BucketList.query.get_or_404(bucketlist_id)
            db.session.query(BucketListItem).filter(
                BucketListItem.id == item_id).update({'done': True})
            db.session.commit()
            return {'here': 'now'}
        else:
            abort(400)

    def delete(self, bucketlist_id, item_id):
        # method handles the delete request to the route
        BucketList.query.get_or_404(bucketlist_id)
        if db.session.query(BucketListItem).filter(
                BucketListItem.id == item_id).delete():
            db.session.commit()
        else:
            abort(400)


class UserRegAPI(Resource):
    '''
    The resource helps registers a new user with the post method.
    '''

    def __init__(self, reqparse=reqparse):
        # parse the request from the client
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', required=True,
            type=str, help="The username is required")
        self.parser.add_argument(
            'password', required=True,
            type=str, help="Password is a required field")
        self.username = self.parser.parse_args().get('username')
        self.password = self.parser.parse_args().get('password')

    def post(self, User=User):
        # call methods to save user data and return success or otherwise
        if (
            self.check_input_validity() and not
                User.query.filter_by(username=self.username.title()).first()):
            user = self.create_new_user()
            if user:
                return user.get('username'), 201
            else:
                abort(400, message='Bad request')
        else:
            abort(400, message='Username in use or invalid username/password')

    def check_input_validity(self):
        # check if there is data supplied
        return True if (
            self.username.isalpha() and self.password.strip()) else False

    def create_new_user(self, User=User, db=db):
        # create a user after checking some conditions
        user = User(self.username.title())
        user.hash_password(self.password)
        if save(user, db):
            return user
        return False


class UserLoginAPI(Resource):
    '''
    Logs in a user to a session
    '''
    # decorators = [auth.login_required]

    def __init__(self, reqparse=reqparse):
        # parse the arguments.
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', required=True, type=str)
        self.parser.add_argument(
            'password', required=True, type=str)
        self.username = self.parser.parse_args().get('username')
        self.password = self.parser.parse_args().get('password')

    def post(self, User=User):
        # parse and
        user = User.query.filter_by(username=self.username).first()
        if user and user.verify_password(self.password):
            token = user.generate_auth_token()
            return {'token': token.decode('ascii')}
        else:
            abort(404, message='Invalid username and password')

    def check_data_validity(self):
        # check if there is data supplied
        return True if (
            self.username.isalpha() and self.password.strip()) else False


api = Api(app)
api.add_resource(
    BucketListAPI,"/bucketlists/","/bucketlists/<int:bucketlist_id>", endpoint='bucketlist_id')
api.add_resource(BucketListItemView, "/bucketlists/<int:bucketlist_id>/items/", "/bucketlists/<int:bucketlist_id>/items/<int:item_id>")
api.add_resource(UserRegAPI, "/auth/register")
api.add_resource(UserLoginAPI, "/auth/login")

if __name__ == '__main__':
    app.run(debug=True)
