#!/usr/bin/env python

from flask_sqlalchemy import SQLAlchemy
from views import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/bucketlist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class Base(db.Model):
    '''
    Base class contains data that is common to
    the User and Bucketlist models i.e
    id which is the primary key, date created
    and date modified
    '''
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)
    date_modified = db.Column(db.DateTime)


class User(Base):
    '''
    This model holds data for a User i.e.
    A user ID, a hash_password for verification and
    a relationship to a user's bucketlists
    '''
    __tablename__ = 'users'
    password = db.Column(db.String(32))
    bucket_lists = db.relationship('BucketList', backref='user',
                                   cascade='all, delete-orphan')

    def __init__(self, created_by, hash_password):
        self.created_by = created_by
        self.hash_password = hash_password

    def __repr__(self):
        return '<Created by {}>'.format(self.created_by)


class BucketList(Base):
    '''
    This is the one stop data place for
    a single bucketlist.
    '''
    __tablename__ = 'bucket_lists'
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    bucket_lists_items = db.relationship('BucketListItem',
                                         backref='bucketlist',
                                         cascade='all, delete-orphan')

    def __init__(self, bucketlistname):
        self.bucket_list_name = bucketlistname

    def __repr__(self):
        return '<BucketList {}>'.format(self.bucket_list_name)


class BucketListItem(Base):
    '''
    This is the data center for a single
    item in the bucket list
    '''
    __tablename__ = 'items'
    done = db.Column(db.Boolean)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(
        BucketList.id))

    def __init__(self, bucket_list_item_name, done=False):
        self.bucket_list_item_name = bucket_list_item_name
        self.done = done

    def __repr__(self):
        return '<BucketListItem {}>'.format(self.item_name)
