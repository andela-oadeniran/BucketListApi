from flask_restful import Api
from utils import app
from resources import (
    BucketListAPI, BucketListItemAPI, UserRegAPI, UserLoginAPI)


api = Api(app, prefix='/api/v1/')


api.add_resource(UserRegAPI, "/auth/register")
api.add_resource(UserLoginAPI, "/auth/login")
api.add_resource(BucketListAPI, "/bucketlists",
                 "/bucketlists/",
                 "/bucketlists/<int:bucketlist_id>")
api.add_resource(
    BucketListItemAPI, "/bucketlists/<int:bucketlist_id>/items",
    "/bucketlists/<int:bucketlist_id>/items/",
    "/bucketlists/<int:bucketlist_id>/items/<int:item_id>")


@app.route('/', methods=['GET'])
def home_page():
    return 'Welcome to BucketList API Home. '\
        'Register and Login to start using the Service'


@app.errorhandler(404)
def handle_error(message):
    return "Resource not found", 404

app.run(debug=True)