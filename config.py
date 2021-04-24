import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'lbms.db')
    BOOTSTRAP_SERVE_LOCAL=True
    RENT_FEE = 500
    DEBT_LIMIT = 500
    PER_PAGE_COUNT = 10

