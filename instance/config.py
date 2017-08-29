import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEFAULT_PAGINATION_LIMIT = 20
    MAXIMUM_PAGINATION_LIMIT = 100

class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True


class TestingConfig(Config):
    """Configurations for Testing, it has its own database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/test_db'
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://ruybwyovidomdq:ebc72b1495e5e5f3f3c0badcfd279fdfe17624a4d7387c3d0c0e2ee2233f997f@ec2-107-22-211-182.compute-1.amazonaws.com:5432/d2rrklu5e9n72i'


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgres://kkolmsmoopltcf:21ae474621e9d2156f04b547e9b2cfcef584d83eb8b55c663f93d07bbbde40ab@ec2-107-22-211-182.compute-1.amazonaws.com:5432/d9ra0tvddslop0'
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
