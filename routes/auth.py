import json
import functools
from core import messages
from flask_login import login_user, logout_user
from school_manager.models.user import User
from werkzeug.security import check_password_hash
from flask import (Blueprint, g, request, session, jsonify, redirect)
from school_manager.db import db
from school_manager.constants import models_fields

bp = Blueprint('auth', __name__, url_prefix='/auth')

INCORRECT_CREDENTIALS_MESSAGE = "Incorrect username or password. Please try again."
LOGIN_SUCCESS_MESSAGE = "User logged in successfully"
LOGIN_FAILED_MESSAGE = "Login failed"

LOGOUT_SUCCESS = "User logged out successfully"
LOGOUT_FAIL = "Logout failed"


@bp.route('/login', methods=('get', 'post'))
def login():
    if request.method == 'POST':
        login_data = request.json
        user = User.read(many=False, username=login_data["username"], deleted=False)
        if not user or not check_password_hash(user["password"], login_data["password"]):
            return jsonify({messages.STR_ERROR: True, messages.STR_MESSAGE: INCORRECT_CREDENTIALS_MESSAGE})

        from flask_login import login_user
        user = User(**user)
        if login_user(user, remember=login_data['remember_me'], force=True):
            return jsonify({messages.STR_ERROR: False, messages.STR_MESSAGE: LOGIN_SUCCESS_MESSAGE})

        return jsonify({messages.STR_ERROR: True, messages.STR_MESSAGE: LOGIN_FAILED_MESSAGE})
    else:
        return redirect('/index.html')


@bp.route('/logout')
def logout():
    from flask_login import logout_user
    if logout_user():
        return jsonify({messages.STR_ERROR: False, messages.STR_MESSAGE: LOGOUT_SUCCESS})

    return jsonify({messages.STR_ERROR: True, messages.STR_MESSAGE: LOGOUT_FAIL})


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        results = User.read(id=user_id, deleted=False)
        g.user = results[0] if results else None
        # End the transaction started by User.read - Must
        db.session.commit()


def login_required():
    """
    Attribute decorator for routes to require a log on for accessing the route
    :return: The wrapped function
    """
    def wrapper(func):
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            from flask.globals import current_app
            if g.user is None:
                return current_app.login_manager.unauthorized()

            return func(*args, **kwargs)

        return decorated_view

    return wrapper


def role_required(roles):
    """
    Attribute decorator for routes to require a log on for accessing the route
    :param roles: Roles eligible for accessing the route
    :return: The wrapped function
    """
    def wrapper(func):
        @functools.wraps(func)
        def decorated_view(*args, **kwargs):
            from flask_login import current_user
            from flask.globals import current_app

            if g.user:
                user = g.user
                if current_user and models_fields.ROLE in user.keys() and user[models_fields.ROLE] in roles:
                    return func(*args, **kwargs)

            return current_app.login_manager.unauthorized()

        return decorated_view

    return wrapper
