# from bucketlist import db
import os
import sys
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from bucketlistapi import app, db
from webargs import fields, validate

user_reg_login_field = {
    'username': fields.Str(required=True, validate=validate.Length(8)),
    'password': fields.Str(required=True, validate=validate.Length(8))
}

name_field = {
    'name': fields.Str(required=True, validate=validate.Length(10))
}

name_done_field = {
    'name': fields.Str(validate=validate.Length(10)),
    'done': fields.Bool()
}

limit_field = {
    'limit': fields.Int(),
    'page': fields.Int(),
    'q': fields.String()
}


def save(obj):
    # adds a valid instance to the session
    try:
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False
