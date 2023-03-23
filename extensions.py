from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os


login_manager = LoginManager()
db = SQLAlchemy()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/users_pictures')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}