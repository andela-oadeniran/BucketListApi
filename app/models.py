#!/usr/bin/env python

from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
from utilities import format_time_stamp
from bucketlist import db


class Base(db.Model):
    '''
    Base class contains data that is common to
    the User and Bucketlist models i.e
    id which is the primary key, date created
    and date modified
    '''
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)


class User(Base):
    '''
    This model holds data for a User i.e.
    A user ID, a hash_password for verification and
    a relationship to a user's bucketlists
    '''
    password = db.Column(db.String(32))
    bucket_lists = db.relationship('BucketList', backref='user',
                                   cascade='all, delete-orphan')

    def __init__(self, name, hash_password):
        self.name = name
        self.hash_password = hash_password

    def __repr__(self):
        return '<Created by {}>'.format(self.created_by)


class BucketList(Base):
    '''
    This is the one stop data place for
    a single bucketlist.
    '''
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    bucket_lists_items = db.relationship('BucketListItem',
                                         backref='bucketlist',
                                         cascade='all, delete-orphan')
    date_modified = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, bucketlistname, created_by):
        self.name = bucketlistname
        self.date_created = datetime.now()
        self.date_modified = None
        self.items = []
        self.created_by = created_by

    def __repr__(self):
        return '<BucketList {}>'.format(self.name)


class BucketListItem(Base):
    '''
    This is the data center for a single
    item in the bucket list
    '''
    done = db.Column(db.Boolean)
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(
        BucketList.id))
    date_modified = db.Column(
        db.DateTime, default=datetime.now(), onupdate=datetime.now)

    def __init__(self, bucket_list_item_name,
                 date_modified=None, done=False):
        self.bucket_list_item_name = bucket_list_item_name
        self.date_created = format_time_stamp(datetime.now)
        self.date_modified = date_modified
        self.done = done

    def __repr__(self):
        return '<BucketListItem {}>'.format(self.item_name)


