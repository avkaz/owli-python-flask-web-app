from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(15), unique = True)
    nickname = db.Column(db.String(10), unique = False)
    email = db.Column(db.String(50), unique = True)
    hashed_password = db.Column(db.String(80))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    registered = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    
    quizzes = db.relationship("Quiz", backref="user", lazy=True, cascade='all, delete, delete-orphan')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password, method='sha256')
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    def __repr__(self):
        return f"<User {self.username}>"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer, default = 15)
    public = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)

    results = db.relationship("Result", backref="quiz", lazy=True)
    questions = db.relationship("Question", backref="quiz", lazy=True, cascade='all, delete, delete-orphan')
    session = db.relationship("Session", backref="quiz", lazy=True, cascade='all, delete, delete-orphan')

    def question_count(self):
        return len(self.questions)
        
    def __repr__(self):
        return f"<Quiz {self.title}>"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    text = db.Column(db.String(150), nullable=False)
    image_url = db.Column(db.String(200))

    choices = db.relationship("Choice", backref="question", lazy=True, cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"<Question {self.text}>"

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    text = db.Column(db.String(80), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)


    def __repr__(self):
        return f"<Choice {self.text}>"

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_code = db.Column(db.Integer, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    questions_list = db.Column(db.Text)
    results = db.relationship("Result", backref="session", lazy=True, cascade='all, delete, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    response_id = db.Column(db.Integer, unique =True )
    question_index = db.Column(db.Integer)
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))




    def __repr__(self):
        return f"<Result for user {self.user_id} on session {self.session_id} of quiz {self.quiz_id}: {self.score}>"
    

    def __repr__(self):
        return f"<Result for user {self.user_id} on quiz {self.session_id}: {self.score}>"
