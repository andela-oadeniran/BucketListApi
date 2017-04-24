from collections import OrderedDict
from flask import g, request
from flask_httpauth import HTTPTokenAuth
from flask_restful import abort, Resource
from sqlalchemy import and_
from webargs.flaskparser import use_args


from bucketlistapi.utils import (user_reg_login_field, name_field,
                                 name_done_field, limit_field, save)
from bucketlistapi.models import BucketList, BucketListItem, User
from bucketlistapi import db

auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token):
    token = request.headers.get('Token')
    if not token:
        return False
    user = User.verify_auth_token(token)
    if not user:
        return False
    g.user = user
    return True


class UserRegAPI(Resource):
    '''
    The resource helps registers a new user with the post method.
    [POST]

    params: username and password.
    '''

    @use_args(user_reg_login_field)
    def post(self, args):
        # call methods to save user data and return success or otherwise
        self.username = args.get('username')
        self.password = args.get('password')
        self.__check_valid_data()
        user = self.__create_new_user()
        return user.as_dict(), 201 if self.save_user(user) else abort(
            400, message='Request could not be processed!')

    def __check_valid_data(self):
        # check for edge cases and return valid error
        if self.__check_user_exists():
            abort(400, message='username already exists')
        elif not (self.__check_username() and self.__check_password()):
            abort(400, message='username/password minimum length is 4/8')
        else:
            pass

    def __check_username(self):
        # username must be at leasr 4 characters long
        return len(self.username.strip()) > 4

    def __check_password(self):
        # password minimum length is 7
        return len(self.password.strip()) > 7

    def __create_new_user(self):
        # create a user an instance of the User Model
        user = User(self.username.title().strip(), self.password)
        user.hash_password()
        return user

    def __check_user_exists(self):
        # should return an error message if user exists
        return User.query.filter_by(
            username=self.username.strip().title()).first()

    @staticmethod
    # save a user in the database using the save() utilitity
    def save_user(user):
        return save(user)


class UserLoginAPI(Resource):
    '''
    Logs in a user to a session
    '''
    @use_args(user_reg_login_field)
    def post(self, args):
        # Return token for valid user
        self.username = args.get('username')
        self.password = args.get('password')
        user = self.__verify_user()
        token = self.generate_auth_token(user)
        return {'token': token.decode('ascii')}, 200

    def __verify_user(self):
        # verify a user's detail's
        user = self.__get_user()
        return user if (
            user and user.verify_password(self.password)) else abort(
            404, message="Invalid username/password")

    @staticmethod
    def generate_auth_token(user):
        # generate token and return
        return user.generate_auth_token()

    def __get_user(self):
        # get user with the username and password
        return User.query.filter_by(
            username=self.username.strip().title()).first()


class BucketListAPI(Resource):
    '''
    The class for the bucket list resource
    POST : To create a new Bucket List
    GET : To retrieve the list of all bucketlists.
    GET : Retrieve a single bucket list
    PUT: To update a single bucket list.
    DELETE: To remove a bucket list

    params:
    [POST] bucketlist 'name', location json body
    [PUT] buckelistname or done location json body
    [GET] limit, name search(q), query string
    '''
    decorators = [auth.login_required]

    def __init__(self):
        self.created_by = g.user.id

    @use_args(name_field)
    def post(self, args, bucketlist_id=None):
        # This handles the creation of a new bucketlist
        if bucketlist_id:
            abort(405, message="method not supported for the URL")
        self.name = args.get('name')  # self.parser.parse_args().get('name')
        if not self.check_bucketlist_name():
            abort(400,
                  message='Bucketlist name must be at least 8 characters')
        elif self.bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        else:
            bucketlist = BucketList(self.name.strip().title(), self.created_by)
            if save(bucketlist):
                return bucketlist.as_dict(), 201  # return a serialized objedct
            return abort(400, message='Could not save the request!!!')

    @use_args(limit_field)
    def get(self, args, bucketlist_id=None):
        # get the list of bucket lists or an item and return.
        if bucketlist_id:
            # return the bucketlist with the bucketlist id specified
            bucketlist = self.get_a_single_bucketlist(bucketlist_id)
            return bucketlist.as_dict(), 200
        else:
            # implement pagination for name search or bucketlists for user
            limit = args.get('limit', 20) if (
                args.get('limit', 20) < 100) else 100
            page = args.get('page', 1)
            name_search = args.get('q')
            bucketlists = g.user.bucketlists
            if not bucketlists.all():
                return abort(
                    404, message='You don\'t have any bucketlist yet!')
            if name_search:
                bucketlists = bucketlists.filter(
                    BucketList.name.ilike("%{}%".format(name_search.title())))
            if not bucketlists.all():
                abort(
                    404, message='no bucketlist containing {}'
                    .format(name_search))
            resp = self.paginate(bucketlists, page, limit, request.url_root)
            return {
                'data': resp[0],
                'pages': resp[1],
                'previous_page': resp[2],
                'next_page': resp[3]
            }, 200

    @use_args(name_field)
    def put(self, args, bucketlist_id=None):
        # update a bucketlist with id(bucketList_id)
        if not bucketlist_id or not (
                BucketList.query.get(
                    bucketlist_id).created_by == self.created_by):
            abort(405, message='method not supported for'
                  ' the URL or invalid bucketlist id.')
        self.name = args.get('name')
        if not self.check_bucketlist_name():
            abort(400, message='name field cannot be empty or too short')
        elif self.bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        elif self.update_bucketlist(bucketlist_id):
            db.session.commit()
            return BucketList.query.get(bucketlist_id).as_dict()
        abort(400, message='Could not update bucketlist {}'.format(
            bucketlist_id))

    def delete(self, bucketlist_id=None):
        # method view to delete a bucket list with the associated id
        if not bucketlist_id:
            abort(405, message='method not supported for the URL')
        if self.delete_bucketlist(bucketlist_id):
            db.session.commit()
            return 'successfully deleted bucketlist {}'.format(
                bucketlist_id), 200
        else:
            abort(
                404, message='Bucketlist {} does not exist'.format(
                    bucketlist_id))

    def check_bucketlist_name(self):
        # bucketlist name must satisfy the condition
        return len(self.name.strip()) > 9

    def bucket_list_name_exists(self):
        bucketlist = BucketList.query.filter_by(
            name=self.name.strip().title()).first()
        return int(bucketlist.created_by) == self.created_by if (
            bucketlist) else False

    def delete_bucketlist(self, bucketlist_id):
        # delete the bucketlist with bucketlist_id
        return db.session.query(BucketList).filter(
            and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).delete()

    def update_bucketlist(self, bucketlist_id):
        # for the PUT method update the bucketlist
        return db.session.query(
            BucketList).filter(and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).update(
                {'name': self.name.strip().title()})

    @staticmethod
    def paginate(bucketlists, page, limit, url_root):
        # paginate the queried object containing bucketlists
        bucketlists = bucketlists.paginate(
            page=page, per_page=limit, error_out=False)
        prev_page = str(url_root) +\
            'api/v1/bucketlists?' + 'limit=' + str(limit) + '&page=' +\
            str(page - 1) if bucketlists.has_prev else None
        next_page = str(
            url_root) + 'api/v1/bucketlists?' + 'limit=' +\
            str(limit) + '&page=' + str(page + 1) if (
            bucketlists.has_next) else None
        bucketlists_per_page = OrderedDict([('Bucketlist{}'.format(
            bucketlist.id), bucketlist.as_dict())
            for bucketlist in bucketlists.items])
        return [bucketlists_per_page, bucketlists.pages, prev_page, next_page]

    def get_a_single_bucketlist(self, bucketlist_id):
        # return Erro 404 if it does not exist
        return BucketList.query.filter(and_(
            BucketList.created_by == self.created_by,
            BucketList.id == bucketlist_id)).first_or_404()


class BucketListItemAPI(Resource):
    '''
    The class for Items in a bucket list
    POST: creates a new item in the bucketlist
    PUT: updates a bucket list item with an id
    DELETE: Delete the bucket list item with the ID

    params:
    [POST] item_name
    [PUT] item_name or self.done
    '''
    decorators = [auth.login_required]

    def __init__(self):
        self.created_by = g.user.id

    @use_args(name_field)
    def post(self, args, bucketlist_id, item_id=None):
        # method to handle post request
        if item_id:
            abort(405,
                  message='The method is not supported for the requested URL')
        if not self.check_bucket_list_with_user(bucketlist_id):
            abort(404, message='invalid bucketlist id check URL')
        self.item_name = args.get('name')
        if not self.check_item_name():
            abort(400, message='item name required'
                  ' and must have at least 10 characters')
        elif self.check_item_name_with_user():
            abort(400, message='item name already exists')
        else:
            item = BucketListItem(
                self.item_name.strip().title(), bucketlist_id)
            if save(item):
                return item.as_dict(), 201
            else:
                abort(400, message='item name could not be saved')

    @use_args(name_done_field)
    def put(self, args, bucketlist_id, item_id=None):
        # method handles the put request to the resource
        # name = request.args.get('name') or self.done
        if not item_id:
            abort(405,
                  message='The method is not supported for the requested URL')
        elif not (self.check_bucket_list_with_user(bucketlist_id) and
                  self.check_item_id_with_bucketlist(
                item_id, bucketlist_id)):
            abort(404, message='invalid bucketlist/item id in URL')
        self.item_name = args.get('name')
        self.done = args.get('done')
        if (self.check_item_name_with_user()):
            abort(400, message='item name already exists')
        if (self.item_name is not None) and (not self.check_item_name()):
            abort(400, message='invalid item name')
        self.update_item(item_id)
        return BucketListItem.query.get(item_id).as_dict(), 201

    def delete(self, bucketlist_id, item_id=None):
        # method handles the delete request to the route
        if not item_id:
            abort(
                405, message='The method is not'
                ' supported for the requested URL')
        elif not (self.check_bucket_list_with_user(bucketlist_id) and
                  self.check_item_id_with_bucketlist(item_id, bucketlist_id)
                  ):
            abort(404, message='Invalid URL')
        elif db.session.query(BucketListItem).filter_by(id=item_id).delete():
            db.session.commit()
            return 'Successfully deleted Item', 200
        else:
            abort(501, message='Server Error')

    def check_item_name(self):
        # check item name for valiity
        return len(self.item_name.strip()) > 10 if self.item_name else False

    def check_bucket_list_with_user(self, bucketlist_id):
        # current user bucket list returns True
        bucketlist = BucketList.query.get(bucketlist_id)
        return bucketlist.created_by == self.created_by if (
            bucketlist) else False

    @staticmethod
    def check_item_id_with_bucketlist(item_id, bucketlist_id):
        # check the bucketlist item and the bucketlist
        bucketlistitem = BucketListItem.query.get(item_id)
        return int(bucketlistitem.bucketlist_id) == bucketlist_id if (
            bucketlistitem) else False

    def check_item_name_with_user(self):
        bucketlistitem = BucketListItem.query.filter_by(
            name=self.item_name.strip().title()).first() if (
            self.item_name) else False
        if bucketlistitem:
            return BucketList.query.get(
                bucketlistitem.bucketlist_id).created_by == self.created_by
        return False

    def update_item(self, item_id):
        # update the given field
        if self.item_name:
            (db.session.query(BucketListItem).filter_by(
                id=item_id).update(
                {'name': self.item_name.strip().title()}))
        if self.done:
            (db.session.query(BucketListItem).filter_by(
                id=item_id).update(
                {'done': True}))
        db.session.commit()

