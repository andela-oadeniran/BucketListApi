#!/usr/bin/env python
from bucketlist import app, db
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context


class Base(db.Model):
    '''
    Base class contains data that is common to
    the User and Bucketlist models i.e
    id which is the primary key, date created
    and date modified
    '''
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def as_dict(self):
        # unpack model properties as dict values and return
        return {col.name: str(getattr(
            self, col.name))
            for col in self.__table__.columns}


class User(Base):
    '''
    This model holds data for a User i.e.
    A user ID, a hash_password for verification and
    a relationship to a user's bucketlists
    '''
    username = db.Column(
        db.String(256), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    bucket_lists = db.relationship('BucketList', backref='user',
                                   cascade='all, delete-orphan')

    def __init__(self, name):
        self.username = name

    def hash_password(self, password):
        # generate a hash for the password
        self.password_hash = pwd_context.encrypt(password)
        return self.password_hash

    def verify_password(self, password):
        # check password hash matches password.
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
            s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
            return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        # check token to ascertain validity
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def get(self, attr):
        return {
            attr: getattr(self, attr)
        }

    def __repr__(self):
        return '<Created by {}>'.format(self.username)


class BucketList(Base):
    '''
    This is the one stop data place for
    a single bucketlist.
    '''
    created_by = db.Column(db.String, db.ForeignKey('user.id'))
    name = db.Column(db.String(256))
    items = db.relationship('BucketListItem',
                            backref='bucket_list',
                            cascade='all, delete-orphan')

    def __init__(self, bucketlistname, created_by):
        self.name = bucketlistname
        self.created_by = created_by

    def __repr__(self):
        return '<BucketList {}>'.format(self.name)


class BucketListItem(Base):
    '''
    This is the data center for a single
    item in the bucket list
    '''
    done = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(256))
    bucketlist_id = db.Column(db.String, db.ForeignKey(
        'bucket_list.id'))

    def __init__(self, item_name, date_done=False):
        self.name = item_name

    def __repr__(self):
        return '<BucketListItem {}>'.format(self.item_name)


