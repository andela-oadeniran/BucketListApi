import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_URL = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'bucketlist.sqlite')


class BaseConfig(object):
    '''
    The class holds base config for each environment
    '''
    SECRET_KEY = os.getenv('SECRET_KEY', 'This should be changed')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', "'sqlite:///' + {}".format(DB_URL))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # CSRF_ENABLED = True
    ERROR_404_HELP = True
    DEBUG = False
    TESTING = False
    # CSRF_ENABLED = True


class DevelopmentConfig(BaseConfig):
    '''
    configuration for the development environment
    '''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_URL
    DEBUG = True
    DEVELOPMENT = True


class TestingConfig(BaseConfig):
    '''
    config when testing
    '''
    TESTING = True


class StagingConfig(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    '''
    config for when in production
    '''
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    #     BASE_DIR + '.sqlite')
    DEBUG = False
