#!/usr/bin/emv python

#import modules

import sys
import os
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
sys.path.append(APP_DIR)
from views import app, BucketListView, BucketListItemView
from models import User, BucketList, BucketListItem
from utilities import get_item_or_raise_error



