#!/usr/bin/env python
from bucketlist import app, db
from collections import OrderedDict
from flask import g
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, abort, reqparse
from models import BucketList, BucketListItem, User
from sqlalchemy import and_
from utilities import save
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs

limit_field = {
    'limit': fields.Int()
}

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

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True, type=str,
                                 help="bucket list name is required")
        self.parser.add_argument('limit', location='args')
        self.created_by = g.user.username

    def post(self, bucketlist_id=None):
        # This handles the creation of a new bucketlist
        if bucketlist_id:
            abort(404, message="Invalid URL")
        self.name = self.parser.parse_args().get('name')
        if not self.__check_name():
            abort(400,
                  message='Bucketlist name must be at least 8 characters')
        elif self.__bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        else:
            bucketlist = BucketList(self.name.title(), self.created_by)
            if save(bucketlist, db):
                return bucketlist.as_dict(), 201  # return serialize
            return abort(400, message='Could not save the request!!!')

    @use_args(limit_field)
    def get(self, args, bucketlist_id=None):
        # get the list of bucket lists or an item and return.
        if bucketlist_id:
            bucketlist = BucketList.query.filter(and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).first_or_404()
            return bucketlist.as_dict()
        else:
            # limit = args.get('limit', 20)
            bucketlists = BucketList.query.filter_by(
                created_by=self.created_by).paginate(page=1, per_page=1).items
            if bucketlists:
                return OrderedDict(
                    [('Bucketlist{}'.format(
                        bucketlist.id), bucketlist.as_dict())
                        for bucketlist in bucketlists])
            return abort(404, message='You don\'t have any bucketlist yet!')

    def put(self, bucketlist_id=None):
        # update a bucketlist with id(bucketList_id)
        if not bucketlist_id or not (
                BucketList.query.get(
                    bucketlist_id).created_by == self.created_by):
            abort(404, message="Invalid URL")
        self.name = self.parser.parse_args().get('name')
        if not self.__check_name():
            abort(400, message="name field cannot be empty or too short")
        elif self.__bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        elif db.session.query(
            BucketList).filter(and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).update(
                {'name': self.name.title()}):
            db.session.commit()
            return BucketList.query.get(bucketlist_id).as_dict()
        abort(400, message='Could not update bucketlist {}'.format(
            bucketlist_id))

    def delete(self, bucketlist_id=None):
        # view to delete a bucket list with the associated id
        if not bucketlist_id:
            abort(404, message="Invalid URL")
        if db.session.query(BucketList).filter(
            and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).delete():
            db.session.commit()
            return "successfully deleted bucketlist {}".format(bucketlist_id)
        else:
            abort(
                404, message='Bucketlist {} does not exist'.format(
                    bucketlist_id))

    def __check_name(self):
        return len(self.name.strip()) > 7

    def __bucket_list_name_exists(self):
        bucketlist = BucketList.query.filter_by(name=self.name.title()).first()
        return bucketlist.created_by == self.created_by if (
            bucketlist) else False


class BucketListItemAPI(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID
    '''
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'name', type=str, help='Item name is required')
        self.parser.add_argument(
            'done', type=str, help='The done field can only be a boolean')
        self.item_name = self.parser.parse_args().get('name')
        self.done = self.parser.parse_args().get('done')
        self.created_by = g.user.username

    def post(self, bucketlist_id, item_id=None):
        # method to handle post request
        if item_id:
            abort(405,
                  message="The method is not supported for the requested URL")
        elif not self.__check_bucket_list_with_user(bucketlist_id):
            abort(404, message='Invalid bucketlist id in URL')
        elif not self.__check_name():
            abort(400, message="item name required"
                  " and must have at least 10 characters")
        elif self.__check_item_name_with_user():
            abort(400, message="item name already exists")
        else:
            item = BucketListItem(self.item_name.title(), bucketlist_id)
            if save(item, db):
                return item.as_dict(), 201
            else:
                abort(400, message='Item name could not be saved')

    def put(self, bucketlist_id, item_id=None):
        # method handles the put request to the resource
        # name = request.args.get('name') or self.done
        if not item_id:
            abort(405,
                  message="The method is not supported for the requested URL")
        elif not (self.__check_bucket_list_with_user(bucketlist_id) and
                  self.__check_item_id_with_bucketlist(
                item_id, bucketlist_id)):
            abort(404, message='Invalid bucketlist/item id in URL')
        elif (self.__check_name() and not
              self.__check_item_name_with_user() and
              db.session.query(BucketListItem).filter_by(
                id=item_id).update({'name': self.item_name.title()})):
            db.session.commit()
            return BucketListItem.query.get(item_id).as_dict()
        elif (self.__check_done() and
              db.session.query(BucketListItem).filter_by(
                id=item_id).update({'done': True})):
            db.session.commit()
            return BucketListItem.query.get(item_id).as_dict()
        else:
            abort(400, message='bad request')

    def delete(self, bucketlist_id, item_id=None):
        # method handles the delete request to the route
        if not item_id:
            abort(
                405, message="The method is not"
                " supported for the requested URL")
        elif not (self.__check_bucket_list_with_user(bucketlist_id) and
                  self.__check_item_id_with_bucketlist(item_id, bucketlist_id)
                  ):
            abort(404, message="Invalid URL")
        elif db.session.query(BucketListItem).filter_by(id=item_id).delete():
            db.session.commit()
            return "Successfully deleted Item"

    def __check_name(self):
        return len(self.item_name.strip()) > 10 if self.item_name else False

    def __check_done(self):
        return self.done.lower() == 'true' if self.done else False

    def __check_bucket_list_with_user(self, bucketlist_id):
        bucketlist = BucketList.query.get(bucketlist_id)
        return bucketlist.created_by == self.created_by if (
            bucketlist) else False

    @staticmethod
    def __check_item_id_with_bucketlist(item_id, bucketlist_id):
        # check the bucketlist item and the bucketlist
        bucketlistitem = BucketListItem.query.get(item_id)
        return int(bucketlistitem.bucketlist_id) == bucketlist_id if (
            bucketlistitem) else False

    def __check_item_name_with_user(self):
        bucketlistitem = BucketListItem.query.filter_by(
            name=self.item_name.title()).first()
        if bucketlistitem:
            return BucketList.query.get(
                bucketlistitem.bucketlist_id).created_by == self.created_by
        return False


class UserRegAPI(Resource):
    '''
    The resource helps registers a new user with the post method.
    '''

    def __init__(self):
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

    def post(self):
        # call methods to save user data and return success or otherwise
        if self.__check_input_validity():
            user = self.__create_new_user()
            if user:
                return user.get('username'), 201
            else:
                abort(400, message='Username not Available')
        else:
            abort(400, message='Invalid Username/Password')

    def __check_input_validity(self):
        # check if there is data supplied
        return True if (
            self.username.isalpha() and self.password.strip()) else False

    def __create_new_user(self):
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

    def __init__(self):
        # parse the arguments.
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', required=True,
            type=str, help="Please input a Username")
        self.parser.add_argument(
            'password', required=True, type=str,
            help="Please input a password")
        self.username = self.parser.parse_args().get('username')
        self.password = self.parser.parse_args().get('password')

    def post(self, User=User):
        # parse and
        user = User.query.filter_by(username=self.username.title()).first()
        if user and user.verify_password(self.password):
            token = user.generate_auth_token()
            return {'token': token.decode('ascii')}
        else:
            abort(404, message='Invalid username/password')


api = Api(app)
api.add_resource(BucketListAPI, "/bucketlists",
                 "/bucketlists/",
                 "/bucketlists/<int:bucketlist_id>")
api.add_resource(
    BucketListItemAPI, "/bucketlists/<int:bucketlist_id>/items",
    "/bucketlists/<int:bucketlist_id>/items/",
    "/bucketlists/<int:bucketlist_id>/items/<int:item_id>")
api.add_resource(UserRegAPI, "/auth/register")
api.add_resource(UserLoginAPI, "/auth/login")

if __name__ == '__main__':
    app.run(debug=True)
