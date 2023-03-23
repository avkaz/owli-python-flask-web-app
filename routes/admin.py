from flask import Blueprint, flash, redirect, render_template, request, url_for, abort
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user, login_required
from models import User, Quiz,Session
from extensions import db
adm = Blueprint('adm', __name__)

@adm.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.admin:
        abort(403)

    page = request.args.get(get_page_parameter(), type=int, default=1)
    users = User.query.order_by(User.id.desc())
    registered_userss = User.query.filter_by(registered=True)
    registered_users = User.query.filter_by(registered=True).all()

# Count the number of registered users
    total_registered_users = len(registered_users)

# Get the last player who is not registered
    last_player = User.query.filter_by(registered=False).order_by(User.id.desc()).first()
    last_player_id = last_player.id if last_player else None

# Count the number of players who are not registered
    total_players = last_player_id - total_registered_users if last_player_id is not None else 0

# Get the ID of the last session
    last_session = Session.query.order_by(Session.id.desc()).first()
    total_sessions = last_session.id if last_session else None

# Get the ID of the last quiz
    last_quiz = Quiz.query.order_by(Quiz.id.desc()).first()
    total_quizzes = last_quiz.id if last_quiz else None

    pagination = Pagination(page=page, total=users.count(), per_page=222)

    return render_template('admin.html', users=registered_userss.paginate(page=page, per_page=222), pagination=pagination, total_users= total_registered_users, total_players = total_players, total_quizzes=total_quizzes, total_sessions=total_sessions)


@adm.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.admin:
        abort(403) # Forbidden

    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('adm.admin'))

    db.session.delete(user)
    db.session.commit()

    flash(f'{user.username} has been deleted', 'success')
    return redirect(url_for('adm.admin'))

@adm.route('/users/admin/<int:user_id>/<int:admin>')
@login_required
def set_admin(user_id, admin):
    if not current_user.admin:
        abort(403) # Forbidden

    user = User.query.get(user_id)
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('adm.admin'))

    user.admin =bool(admin)
    db.session.commit()

    flash(f'{user.username} is now an admin.' if admin else f'{user.username} is no longer an admin.', 'success')
    return redirect(url_for('adm.admin'))




