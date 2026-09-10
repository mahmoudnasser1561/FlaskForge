import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    FLASKY_MAIL_SUBJECT_PREFIX = 'StaffRoom'
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_NOTIFICATIONS_PER_PAGE = 20
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'memory://')
    CACHE_TYPE = 'RedisCache' if os.environ.get('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', '')
    CACHE_DEFAULT_TIMEOUT = 60
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')


    @staticmethod
    def init__app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    CACHE_TYPE = 'NullCache'
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


