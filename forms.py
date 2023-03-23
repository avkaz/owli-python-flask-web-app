from wtforms import StringField, PasswordField, BooleanField, TextAreaField, FileField,SelectField,IntegerField, SelectField
from wtforms.validators import InputRequired, Email, Length
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    username = StringField('username or email', validators=[InputRequired(), Length(min = 4, max = 50)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max = 80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(max = 50)])
    username = StringField('username', validators=[InputRequired(), Length(min = 4, max = 15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max = 80)])

class StudentLoginForm(FlaskForm):
    nickname = StringField('username', validators=[InputRequired(), Length(min = 1, max = 50)])


class QuestionForm(FlaskForm):
    quiz = SelectField('Quiz', coerce=int)
    image = FileField('Image') 
    question = StringField('Question', validators=[DataRequired()])
    answer1 = StringField('Answer 1', validators=[DataRequired()])
    answer2 = StringField('Answer 2', validators=[DataRequired()])
    answer3 = StringField('Answer 3', validators=[DataRequired()])
    answer4 = StringField('Answer 4', validators=[DataRequired()])
    correct_answer = BooleanField('correct_answer')

    
class QuizForm(FlaskForm):
    quizTitle = StringField('Title', validators=[DataRequired()])
    quizDescription = TextAreaField('Description')
    quizDuration = SelectField('Duration', coerce=int, validators=[DataRequired()], choices=[
        (15, '15 seconds'),
        (30, '30 seconds'),
        (45, '45 seconds'),
        (60, '60 seconds'),
        (90, '90 seconds'),
        (120, '120 seconds')
    ])

    
class QuizCodeForm(FlaskForm):
    quiz_code = IntegerField('Quiz Code', validators=[DataRequired()])

