from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from forms import LoginForm, RegisterForm
from datetime import datetime
from sqlalchemy import or_
from extensions import db
from models import User



auth= Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Instantiate LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        # Check if the user entered a valid username or email
        user = User.query.filter(or_(User.username == form.username.data,
                                     User.email == form.username.data)).first()

        if user and user.check_password(form.password.data):
            # Log in the user and update their last login time
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            # Redirect the user to the main index page
            return redirect(url_for('main.index'))

        # Flash an error message if the username or password is invalid
        flash('Invalid username or password', 'error')

    # Render the login page with the LoginForm
    return render_template('login.html', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Instantiate RegisterForm
    form = RegisterForm()

    # Check if the 'filled' argument is in the request
    filled = request.args.get('filled')
    if filled is None:
        filled = False

    if form.validate_on_submit():
        try:
            # Create a new User object with the submitted data
            new_user = User(username=form.username.data, email=form.email.data, admin=False, registered=True)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            # Flash a success message if the new user was created successfully
            flash('New user has been created', 'success')
            return redirect(url_for('main.index'))
        except:
            # Roll back the session and flash an error message if the username or email already exists
            db.session.rollback()
            flash('Mail or Username already exists', 'error')

    # Render the signup page with the RegisterForm and 'filled' argument
    return render_template('signup.html', form=form, filled=filled)


@auth.route('/logout')
@login_required
def logout():
    # Log out the user and redirect to the main index page
    logout_user()
    return redirect(url_for('main.index'))
