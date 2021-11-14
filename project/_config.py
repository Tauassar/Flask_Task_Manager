import os

# Directory of the script
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'my_precious'
DEBUG = True

# full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
