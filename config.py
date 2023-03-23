import os 
from extensions import db
SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
SECRET_KEY = os.environ.get('eonjwcilwn9283y87KJBpoidhOUHBD91823uy')
SQLALCHEMY_TRACK_MODIFICATIONS = False
