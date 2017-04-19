from collections import OrderedDict
from flask import g, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import abort, Resource
from sqlalchemy import and_
from webargs.flaskparser import use_args
from utils import (
    db, user_reg_login_field, name_field,
    name_done_field, limit_field, save)
from models import BucketList, BucketListItem, User


# api = Api(app)

auth = HTTPBasicAuth()


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
        if self.check_user_exists():
            abort(400, message='username already exists')
        if (self.check_name() and
                self.check_password()):
            user = self.create_new_user()
            return user.as_dict(), 201 if self.save_user(user) else abort(
                400, message='bad request')
        else:
            abort(400, message='username/password minimum length is 8')

    def check_name(self):
        return self.username.isalpha() and (len(self.username.strip()) > 7)

    def check_password(self):
        return len(self.password.strip()) > 7

    def create_new_user(self):
        # create a user an instance of the User Model
        user = User(self.username.title().strip(), self.password)
        user.hash_password()
        return user

    def check_user_exists(self):
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
        user = User.query.filter_by(
            username=self.username.strip().title()).first()
        if user and user.verify_password(self.password):
            token = user.generate_auth_token()
            return {'token': token.decode('ascii')}
        else:
            abort(404, message='Invalid username/password')


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
        self.created_by = int(g.user.id)

    @use_args(name_field)
    def post(self, args, bucketlist_id=None):
        # This handles the creation of a new bucketlist
        if bucketlist_id:
            abort(404, message="method not supported for the URL")
        self.name = args.get('name')  # self.parser.parse_args().get('name')
        if not self.check_name():
            abort(400,
                  message='Bucketlist name must be at least 8 characters')
        elif self.bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        else:
            bucketlist = BucketList(self.name.strip().title(), self.created_by)
            if save(bucketlist):
                return bucketlist.as_dict(), 201  # return serialize
            return abort(400, message='Could not save the request!!!')

    @use_args(limit_field)
    def get(self, args, bucketlist_id=None):
        # get the list of bucket lists or an item and return.
        if bucketlist_id:
            # return the bucketlist with the bucketlist id specified
            bucketlist = BucketList.query.filter(and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).first_or_404()
            return bucketlist.as_dict()
        else:
            # implement pagination for name search or bucketlists for user
            limit = args.get('limit', 20) if (
                args.get('limit', 20) < 100) else 100
            page = args.get('page', 1)
            name_search = args.get('q')
            bucketlists = g.user.bucketlists
            if name_search:
                bucketlists = bucketlists.filter(
                    BucketList.name.ilike("%{}%".format(name_search.title())))
            if not bucketlists.all():
                abort(
                    404, message='no bucketlist containing {}'
                    .format(name_search))
            bucketlists = bucketlists.paginate(
                page=page, per_page=limit, error_out=False)
            prev_page = str(request.url_root) +\
                'bucketlists?' + 'limit=' + str(limit) + '&page=' +\
                str(page - 1) if bucketlists.has_prev else None
            next_page = str(request.url_root) + 'bucketlists?' + 'limit=' +\
                str(limit) + '&page=' + str(page + 1) if (
                bucketlists.has_next) else None
            bucketlists_per_page = OrderedDict([('Bucketlist{}'.format(
                bucketlist.id), bucketlist.as_dict())
                for bucketlist in bucketlists.items])
            if bucketlists_per_page:
                return {
                    "data": bucketlists_per_page,
                    "pages": bucketlists.pages,
                    "previous_page": prev_page,
                    "next_page": next_page
                }
            return abort(404, message='You don\'t have any bucketlist yet!')

    @use_args(name_field)
    def put(self, args, bucketlist_id=None):
        # update a bucketlist with id(bucketList_id)
        if not bucketlist_id or not (
                BucketList.query.get(
                    bucketlist_id).created_by == str(self.created_by)):
            abort(404, message="method not supported for the URL.")
        self.name = args.get('name')
        if not self.check_name():
            abort(400, message="name field cannot be empty or too short")
        elif self.bucket_list_name_exists():
            abort(400, message='Bucket List name already exists')
        elif db.session.query(
            BucketList).filter(and_(
                BucketList.created_by == self.created_by,
                BucketList.id == bucketlist_id)).update(
                {'name': self.name.strip().title()}):
            db.session.commit()
            return BucketList.query.get(bucketlist_id).as_dict()
        abort(400, message='Could not update bucketlist {}'.format(
            bucketlist_id))

    def delete(self, bucketlist_id=None):
        # view to delete a bucket list with the associated id
        if not bucketlist_id:
            abort(404, message="method not supported for the URL")
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

    def check_name(self):
        return len(self.name.strip()) > 7

    def bucket_list_name_exists(self):
        bucketlist = BucketList.query.filter_by(
            name=self.name.strip().title()).first()
        return int(bucketlist.created_by) == self.created_by if (
            bucketlist) else False


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
        if not self.check_name():
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
            abort(404, message='Invalid bucketlist/item id in URL')
        self.item_name = args.get('name')
        self.done = args.get('done')
        if self.check_name() and not self.check_item_name_with_user():
            abort(400, message='item name exists or is invalid')
        if (db.session.query(BucketListItem).filter_by(
                id=item_id).update({'name': self.item_name.strip().title()})):
            db.session.commit()
        if (self.done and db.session.query(BucketListItem).filter_by(
                id=item_id).update({'done': True})):
            db.session.commit()
        return BucketListItem.query.get(item_id).as_dict()

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
            return 'Successfully deleted Item'
        else:
            abort(501, message='Server Error')

    def check_name(self):
        return len(self.item_name.strip()) > 10 if self.item_name else False

    def check_done(self):
        return self.done

    def check_bucket_list_with_user(self, bucketlist_id):
        bucketlist = BucketList.query.get(bucketlist_id)
        return int(bucketlist.created_by) == self.created_by if (
            bucketlist) else False

    @staticmethod
    def check_item_id_with_bucketlist(item_id, bucketlist_id):
        # check the bucketlist item and the bucketlist
        bucketlistitem = BucketListItem.query.get(item_id)
        return int(bucketlistitem.bucketlist_id) == bucketlist_id if (
            bucketlistitem) else False

    def check_item_name_with_user(self):
        bucketlistitem = BucketListItem.query.filter_by(
            name=self.item_name.strip().title()).first()
        if bucketlistitem:
            return int(BucketList.query.get(
                bucketlistitem.bucketlist_id).created_by) == self.created_by
        return False





# api.add_resource(UserRegAPI, "/auth/register")
# api.add_resource(UserLoginAPI, "/auth/login")
# api.add_resource(BucketListAPI, "/bucketlists",
#                  "/bucketlists/",
#                  "/bucketlists/<int:bucketlist_id>")
# api.add_resource(
#     BucketListItemAPI, "/bucketlists/<int:bucketlist_id>/items",
#     "/bucketlists/<int:bucketlist_id>/items/",
#     "/bucketlists/<int:bucketlist_id>/items/<int:item_id>")


# @app.route('/', methods=['GET'])
# def home_page():
#     return 'Welcome to BucketList API Home. '\
#         'Register and Login to start using the Service'


# @app.errorhandler(404)
# def handle_error(message):
#     return "Resource not found", 404

# app.run(debug=True)
