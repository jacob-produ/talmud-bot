from flask import request
from school_manager.models.phone_verification import OptVerification
from school_manager.routes.validation_bank_account import create_validation_response_json
from flask import (Blueprint, g, session, jsonify, redirect)
from core import messages
from school_manager.db import db
from school_manager.models.student import Student
import functools
from school_manager.models.user import User

bp_student = Blueprint('auth_student', __name__, url_prefix='/auth_student')

#  Creating variables per message
INCORRECT_CREDENTIALS_MESSAGE = "Incorrect username or password. Please try again."
LOGIN_SUCCESS_MESSAGE = "User logged in successfully"
LOGIN_FAILED_MESSAGE = "Login failed"
LOGOUT_SUCCESS = "User logged out successfully"
LOGOUT_FAIL = "Logout failed"


@bp_student.route('/login_student', methods=('get', 'post'))
def login_student():
    """
        validation of verify code from call2call comparing to user input
        return: JSON including data_token if the code correct
    """
    # Creating default variables that will return in JSON
    message = "ok"
    error = False
    status = "ok"
    data = None

    try:
        #  Get the user input Phone number and code
        user_json = request.get_json()

        #  Saving the values of specific key in a variable
        otp_user_input_code = user_json['code']
        phone_number = user_json['phone_number']

        #  Get the id of the student that the main phone number is phone number for check
        result_student_verify_code = OptVerification.read(many=False, phone_number=phone_number)['verify_code']

        #  Check if the otp user input code is equal to verify code that exist in the DB
        if otp_user_input_code == result_student_verify_code:
            message = "login success"
            error = False
            status = "ok"
            data = None

            # flask login
            result_student = Student.read(many=False, main_phone_number=phone_number)

            if not result_student:
                return jsonify({messages.STR_ERROR: True, messages.STR_MESSAGE: INCORRECT_CREDENTIALS_MESSAGE})

            from flask_login import login_user
            result_student = Student(**result_student)

            if login_user(result_student):
                return jsonify({messages.STR_ERROR: False, messages.STR_MESSAGE: LOGIN_SUCCESS_MESSAGE})
        else:
            message = "something going wrong you can try again or send e-mail to cs@yemot.co.il"
            error = True
            status = "Not ok"

        #  Create a response in JSON format
        response_json = create_validation_response_json(message, error, data, status)


    except Exception as e:
        message = "something going wrong you can try again or send e-mail to cs@yemot.co.il" + str(e)
        error = True
        status = "Not ok"
        #  Create a response in JSON format
        response_json = create_validation_response_json(message, error, data, status)
    return response_json


@bp_student.route('/logout_student')
def logout_student():
    from flask_login import logout_user
    if logout_user():
        return jsonify({messages.STR_ERROR: False, messages.STR_MESSAGE: LOGOUT_SUCCESS})
    return jsonify({messages.STR_ERROR: True, messages.STR_MESSAGE: LOGOUT_FAIL})


@bp_student.before_app_request
def load_logged_in_student():
    student_id = session.get('user_id')
    if student_id is None:
        g.user = None
    else:
        results = Student.read(many=False, id=student_id)
        g.user = results if results else None
        # End the transaction started by User.read - Must
        db.session.commit()


def login_required_student():
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
