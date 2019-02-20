import os

here = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'vnc94nqevnpaidgnf'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or f'sqlite:///{os.path.join(here,"app.db")}?check_same_thread=False'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
