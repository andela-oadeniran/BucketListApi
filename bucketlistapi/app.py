# from flask import request
from flask_restful import Api # abort


from bucketlistapi import app
from bucketlistapi.resources import (
    BucketListAPI, BucketListItemAPI, UserRegAPI, UserLoginAPI)


# @app.before_request
# def only_json():
#     if not request.is_json:
#         abort(400, message='invalid mime type')


@app.route('/', methods=['GET'])
def home_page():
    return 'Welcome to BucketList API Home. '\
        'Register and Login to start using the Service', 200


@app.errorhandler(404)
def handle_error(message):
    return "Resource not found check docs for valid URL endpoints", 404


api = Api(app, prefix='/api/v1')

api.add_resource(UserRegAPI, "/auth/register")
api.add_resource(UserLoginAPI, "/auth/login")
api.add_resource(BucketListAPI, "/bucketlists",
                 "/bucketlists/",
                 "/bucketlists/<int:bucketlist_id>")
api.add_resource(
    BucketListItemAPI, "/bucketlists/<int:bucketlist_id>/items",
    "/bucketlists/<int:bucketlist_id>/items/",
    "/bucketlists/<int:bucketlist_id>/items/<int:item_id>")


