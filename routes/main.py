from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from models import Question, User, Quiz, Result, Session
from forms import  QuizCodeForm, StudentLoginForm
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import generate_csrf
from extensions import db
from flask import make_response
import random
import qrcode
import base64
import json
import io


main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    # Create an instance of the QuizCodeForm class to display on the page
    form = QuizCodeForm()
    
    # Handle form submission if the form passes validation
    if form.validate_on_submit():
        try:
            # Get the quiz session code from the form
            session = form.quiz_code.data
            if not Session.query.filter_by(session_code=session).all():
                flash("There is no Quiz with this code", "error")
                return redirect(url_for('main.index'))
            
            # If the user is authenticated, redirect to the quiz page
            if current_user.is_authenticated:
                return redirect(url_for('main.quiz', session=session))
            # If the user is not authenticated, redirect to the login page
            else:
                return redirect(url_for('main.studentLogin', session=session))
        
        # Catch any errors that occur during execution of the try block
        except Exception as e:
            # Log the error to the console
            print(f"An error occurred: {e}")
            # Return a 500 error response to the user
            return abort(500)

    # If the user is already authenticated, redirect to the quizzes page
    if current_user.is_authenticated:
        return redirect(url_for('crud.quizzes'))

    # Display the index.html page with the form
    return render_template('index.html', form=form)


# When teacher start the quiz

@main.route('/quiz/<int:quiz_id>/start', methods=['GET', 'POST'])
def start_quiz(quiz_id):
    # Retrieve the Quiz object with the given quiz_id from the database, or return a 404 error if it doesn't exist
    quiz = Quiz.query.get_or_404(quiz_id)

    # Create an empty list to store all question dictionaries
    questions_list = []

    # Retrieve all questions for the current quiz from the database
    all_questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Iterate through each question and create a dictionary object for it
    for question in all_questions:
        # Retrieve all choices for the current question using the relationship between Question and Choice models
        all_choices = question.choices

        # Create a list of choice texts for the current question
        choice_texts = [choice.text for choice in all_choices]

        # Create a list of correct choice texts for the current question
        correct_choices = [choice.text for choice in all_choices if choice.is_correct]

        # Randomize the order of the choice texts
        random.shuffle(choice_texts)

        # Create a dictionary object for the current question, including the question text, list of choice texts, and list of correct choice texts
        question_dict = {
            'question_text': question.text,
            'question_image': question.image_url,
            'choices': choice_texts,
            'correct_choices': correct_choices
        }

        # Append the question dictionary to the questions list
        questions_list.append(question_dict)

    # Randomize the order of the questions
    random.shuffle(questions_list)

    # Convert the list of question dictionaries to a JSON string
    questions_json = json.dumps(questions_list)

    # Generate a unique session code
    while True:
        session_code = random.randint(99999, 1000000)

        # Check if the code already exists in the database
        existing_session = Session.query.filter_by(session_code=session_code).first()

        if not existing_session:
            break

    # Create a new session object with the code, quiz id, and list of questions in JSON format
    session = Session(session_code=session_code, quiz_id=quiz.id, questions_list=questions_json)

    # Add the session to the database
    db.session.add(session)
    db.session.commit()

    # Generate a QR code for the session code
    url = "https://owli.cz/studentLogin/{}".format(session_code)
    qr = qrcode.QRCode(version=2, box_size=9, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the image to bytes and encode as base64
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()

    # Render the quiz.html template with the generated code and user information
    return render_template("quiz.html", quiz=quiz, code=session_code, user=current_user, username=current_user.nickname, qr_code=img_base64)


@main.route('/studentLogin/<session>', methods=['GET', 'POST'])
def studentLogin(session):
    logout_user()
    form = StudentLoginForm()
    filled = request.args.get('filled')
    if filled is None:
        filled = False

    # Handle form submission
    if form.validate_on_submit():
        # Create a new user with the nickname provided in the form
        new_user = User(nickname=form.nickname.data, registered=False)

        try:
            # Add the new user to the database
            db.session.add(new_user)
            db.session.commit()

            # Log in the new user and redirect to the quiz page
            login_user(new_user)
            return redirect(url_for('main.quiz', session=session))
        except:
            # If there's an error adding the user to the database, rollback the transaction and show an error message
            db.session.rollback()
            flash('An error occurred while creating the user. Please try again.')
            return redirect(url_for('main.studentLogin', session=session))

    # If the current user is already authenticated, redirect to the quizzes page
    if current_user.is_authenticated:
        return redirect(url_for('crud.quizzes'))

    # Render the student login template with the form and session code
    return render_template('studentLogin.html', form=form, session=session, filled=filled)

#When student connect to the quiz
@main.route('/quiz/<session>', methods=['GET', 'POST'])
def quiz(session):
    # Retrieve the quiz associated with the given session code
    quiz = Quiz.query.join(Session).filter(Session.session_code == session).first()

    # If the quiz cannot be found, show a 404 error page
    if not quiz:
        abort(404)

    # Retrieve the first question in the quiz
    first_question = Question.query.filter_by(quiz_id=quiz.id).first()

    # Render the quiz template with the quiz, session code, first question, and current user
    return render_template('quiz.html', quiz=quiz, code=session, first_question=first_question, user=current_user, username=current_user.nickname)

@main.route('/quiz/<session>/question/<int:question_index>', methods=['GET', 'POST'])
def submit_question(session, question_index):
    # Get the session object for the given session code
    session_obj = Session.query.filter_by(session_code=session).first()

    # Get the quiz object for the current session
    quiz = Quiz.query.get(session_obj.quiz_id)

    # Get the list of questions for the current session as a Python list
    questions_list = json.loads(session_obj.questions_list)

    # Generate a unique response ID for the current user's response to this question
    response_id = int(str(current_user.id) + str(session) + str(question_index))

    # Get the total number of questions in the quiz
    quizlen = len(questions_list)

    # Get the text and image URL for the current question
    question = questions_list[question_index - 1]['question_text']  # Subtract 1 from index
    question_image = questions_list[question_index - 1]['question_image']  # Subtract 1 from index

    # Get the list of choices for the current question
    choices = questions_list[question_index - 1]['choices']  # Subtract 1 from index

    # Get the list of correct choices for the current question
    correct_choices = questions_list[question_index - 1]['correct_choices']  # Subtract 1 from index

    # Set a flag to indicate whether a choice has been selected by the user
    choice_selected = False

    if request.method == 'POST':
        # Get the selected choice from the form
        selected_choice = request.form.get('choice')

        try:
            # Create a new result object for the current user's response to this question
            result = Result(user_id=current_user.id, session_id=session_obj.id, quiz_id=quiz.id,
                            response_id=response_id, question_index=question_index)

            # Check if the selected choice is in the list of correct choices for the current question
            if selected_choice in correct_choices:
                # If the selected choice is correct, set the score for this question to 1
                result.score = 1
            else:
                # If the selected choice is incorrect, set the score for this question to 0
                result.score = 0

            # Add the new result object to the database
            db.session.add(result)
            db.session.commit()

            # Set the choice_selected flag to indicate that a choice has been selected
            choice_selected = True

        except:
            # If there is an error, roll back the database session and display an error message to the user
            db.session.rollback()
            flash("You have already answered this question or there was an error submitting your response", "error")
            return redirect(url_for('main.submit_question', session=session, question_index=question_index, user=current_user))

    # Generate a new CSRF token for the form
    csrf_token = generate_csrf()

    # Render the question template with the appropriate variables
    return render_template('question.html', quiz=quiz, question=question, choices=choices, session=session,
                            question_index=question_index, csrf_token=csrf_token, choice_selected=choice_selected,
                            user=current_user, username=current_user.nickname, quizlen=quizlen,
                            duration=quiz.duration, question_image=question_image, correct_choices=correct_choices)


@main.route('/quiz/<session>/results')
def show_results(session):
    # Retrieve the session object associated with the session code
    session_obj = Session.query.filter_by(session_code=session).first()
    
    # Create an empty dictionary to store user scores
    user_scores = {}
    
    # Retrieve all the results objects associated with the session
    results_obj = Result.query.filter_by(session_id=session_obj.id).order_by(Result.id.asc()).all()
    
    # Iterate through the results objects to retrieve user scores
    for result in results_obj:
        user_id = result.user_id
        user = User.query.get(user_id)
        if user.nickname is not None:
            nickname = user.nickname
            score = result.score
            if nickname not in user_scores:
                user_scores[nickname] = [score]
            else:
                user_scores[nickname].append(score)
    
    # Calculate the total score for each user and sort the dictionary in descending order
    sorted_user_scores = {}
    for nickname, scores in user_scores.items():
        sorted_user_scores[nickname] = sum(scores)
    sorted_user_scores = dict(sorted(sorted_user_scores.items(), key=lambda x: x[1], reverse=True))
    user_scores_list = list(sorted_user_scores.items())
    
    # Print the user scores for debugging purposes
    print(sorted_user_scores)
    
    # Render the results template with the sorted user scores dictionary
    return render_template('results.html', user_scores=sorted_user_scores,user_scores_list=user_scores_list, user =current_user)
