from flask_socketio import SocketIO, join_room, leave_room, send, emit
from models import User, Quiz,Result, Session
from flask_login import current_user
from flask import Blueprint
from extensions import db
import math



socket_blueprint = Blueprint('socketio', __name__)
socketio = SocketIO()
def init_app(app):
    socketio.init_app(app)



def allocate_points(session_obj, question_index, max_points=1000):
    # Get the correct answers for the given question and session
    results = Result.query.filter_by(session_id=session_obj.id, question_index=question_index).filter(Result.score !=0).order_by(Result.id.asc()).all()
    # Calculate the number of correct answers and the total score
    num_correct_answers = len(results)
    
    # Calculate the points to allocate
    if num_correct_answers > 0:
        d = max_points / sum(range(1, num_correct_answers+1))
        points_to_allocate = [math.ceil(d * (num_correct_answers-i+1)) for i in range(num_correct_answers)]
    else:
        points_to_allocate = []
    
    # Allocate points to each correct answer
    for result, points in zip(results, points_to_allocate):
        if num_correct_answers == 1:
            result.score += max_points  # allocate all points to the only correct answer
        else:
            result.score += points - 1  # allocate points according to the algorithm, minus one point for the first answer
    
    # Save the updated results to the database
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    return results



@socketio.on('message')
def handle_message(message):
    room = message['room']
    msg = message['msg']
    username = message['username']
    emit('message', {'msg': msg, 'username': username, 'room':room}, room=room)




@socketio.on("userJoined")
def userJoined(user):
    emit('userJoined', user, broadcast= True)

@socketio.on("startQuiz")
def startQuiz(data):
    room =data['room']
    session = data['session']
    url = "/quiz/{}/question/0?choice_selected=False".format(session)
    emit('redirect', {'url': url, 'currentroom':room}, room=room)

@socketio.on("nextQuestion")
def nextQuestion(data):
    room = data['room']
    session = data['session']
    quizlen = data['quizlen']
    question_index =data['question_index']
    next_question = int(question_index)+1
    if int(question_index)<int(quizlen)-1:
        url = "/quiz/{}/question/{}?choice_selected=False".format(session, next_question)
    else:
        url ="/quiz/{}/results".format(session)
    emit('redirect', {'url': url, 'currentroom':room}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": username + " has joined the " + room + " room.", 'username': username, 'room':room}, room=room)


@socketio.on("leave")
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
   

    print('leave test'+  " "+username + 'left'+ room)
    send({"msg": username + " has left the " + room + " room.", 'username': username, 'room':room}, room=room)



click_counters = {}
#counter of answers
@socketio.on('click')
def handle_click(data):
    room = data['room']
    answerId = data['answerId']
    global click_counters
    if room not in click_counters:
        click_counters[room] = {}  # initialize counter to 0 for new session
    if 'total' not in click_counters[room]:
        click_counters[room]['total'] = 0
    click_counters[room]['total'] += 1
    if answerId not in click_counters[room]:
        click_counters[room][answerId] = 0
    click_counters[room][answerId] += 1
    print(click_counters)
    emit('updateCounter', {'counter': click_counters[room]}, room=room)


@socketio.on("answer")
def answer(data):
    session = data['session']
    room = data['room']
    global click_counters
    click_counters[room] = {}
    session_obj = Session.query.filter_by(session_code=session).first()
    quiz = Quiz.query.get(session_obj.quiz_id)

    question_index =data['question_index']
    response_id = int(str(current_user.id)+str(session)+str(question_index))
    result = Result(user_id=current_user.id, session_id=session_obj.id, quiz_id=quiz.id, response_id =response_id, question_index=question_index)
    result.score = 0
    try:
        db.session.add(result)
        db.session.commit()
    except:
        db.session.rollback()
    allocate_points(session_obj, question_index)
    
    user_scores = {}
    results_obj = Result.query.filter_by(session_id=session_obj.id).order_by(Result.id.asc()).all()
    for result in results_obj:
        user_id = result.user_id
        score = result.score
        if user_id not in user_scores:
            user_scores[user_id] = score
        else:
            user_scores[user_id] += score
    sorted_user_scores = dict(sorted(user_scores.items(), key=lambda x: x[1], reverse=True))
    print(sorted_user_scores)
    print(user_scores)
    print(sorted_user_scores)
    users_list = []
    results_list = []
    for user_id, score in sorted_user_scores.items():
        user = User.query.get(user_id)
        if user.nickname is not None:
            nickname = user.nickname
            users_list.append(nickname)
            results_list.append(score)


    print(users_list)
    print(results_list)

    emit('results',{'users': users_list, 'score':results_list}, room=room)

def register_socketio(app, socketio):
    # Register the socket blueprint with the Flask app
    app.register_blueprint(socket_blueprint)

    # Initialize SocketIO with the Flask app and the socketio object
    socketio.init_app(app, cors_allowed_origins="*", manage_session=False)