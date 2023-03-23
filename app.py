from extensions import db, login_manager, UPLOAD_FOLDER
from datetime import datetime, timedelta
from flask_bootstrap import Bootstrap
from scheduler import run_scheduler
from socket_events import init_app
from models import User, Session
from routes.auth import auth
from routes.main import main
from routes.admin import adm
from routes.crud import crud
from flask import Flask
import schedule
import threading
import config


app = Flask(__name__)
app.config.from_pyfile("config.py")

Bootstrap(app)

login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

#socketIO
init_app(app)

with app.app_context():
    db.create_all()


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

app.register_blueprint(auth)
app.register_blueprint(main) 
app.register_blueprint(adm)
app.register_blueprint(crud)   


#function to delete unregistered users and used sessions
def trash_delete():
    with app.app_context():
        days_ago = datetime.utcnow() - timedelta(days=1)
        unregistered_users = User.query.filter(User.last_login < days_ago).all()
        used_sessions = Session.query.filter(Session.created_at<days_ago).all()
        try:
            for user in unregistered_users:
                if not user.registered:
                    db.session.delete(user)
            db.session.commit()
            print(f"Deleted {len(unregistered_users)} unregistered users")
        except Exception as e:
            print(f"An error occurred while deleting inactive users: {e}")
        try:
            for session in used_sessions:
                db.session.delete(session)
            db.session.commit()
            print(f"Deleted {len(used_sessions)} sessions objects")
        except Exception as e:
            print(f"An error occurred while deleting sessions objects: {e}")
      

# Schedule the task to run every day at 1:00 AM
schedule.every().day.at("01:00").do(trash_delete)

if __name__ == "__main__":
    with app.app_context():
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.start()

    # Start the Flask development server
    app.run(debug=True)