from flask_restful import Resource
from school_manager.routes.validation_bank_account import create_validation_response_json
from flask import request
from school_manager.models.student import Student
import requests
from school_manager.models.phone_verification import OptVerification
from school_manager.db import db


class GetOpt(Resource):
    def post(self):
        """
         Get OPT Api Function
         """
        # Creating default variables that will return in JSON
        data = None
        message = "ok"
        status = "ok"
        error = False

        try:
            # Example of what user_json get: user_json = {'id_number': '312613623', 'id_type': 'תעודת זהות','phone_number': '0544551232'}
            user_json = request.get_json()

            # Saving the values of specific key in a variable
            id_number = user_json['id_number']
            id_type = user_json['id_type']
            phone_number = user_json['phone_number']

            #  Get the id of the student that the main phone number or secondary phone number is phone number for check
            try:
                #  Get the id of the student that the main phone number is phone number for check
                result_student_id = Student.read(many=False, main_phone_number=phone_number)['identity']
                result_student_id_type = Student.read(many=False, main_phone_number=phone_number)['identity_type']

            except Exception as e:
                try:
                    #  Get the id of the student that the secondary phone number is phone number for check
                    result_student_id = Student.read(many=False, secondary_phone_number=phone_number)['identity']
                    result_student_id_type = Student.read(many=False, secondary_phone_number=phone_number)[
                        'identity_type']

                except Exception as e:
                    message = "Invalid input, Error message: " + str(e)

            #  Check if the id number that provided is match to the id that related to the phone number in the db.
            #  Check if the id type that provided is match to the id type that related to the phone number in the db.
            if str(id_number) == str(result_student_id) and str(id_type) == str(result_student_id_type):
                error = False

                #  Send service request to call2call include the phone number
                call2call_response = requests.get(
                    'https://www.call2all.co.il/ym/api/RunTzintuk?token=0773231397:7974455&callerId=RAND&phones=${' + \
                    phone_number + '}')

                #  Save all the JSON field in parameter name call2call_json.
                call2call_json = call2call_response.json()

                #  Check if the status response is Exception
                if call2call_json['responseStatus'] != 'OK':
                    message = 'something going wrong you can try again or send e-mail to cs@yemot.co.il'
                    error = True
                else:
                    message = "We are making a phone call to your phone number and kindly request your attention. " \
                              "The verification code corresponding to the phone call is represented" \
                              " by the final four digits."
                    error = False

                #  Create and write to ths db table
                phone_session = OptVerification()
                phone_session.phone_number = phone_number
                phone_session.response_status = call2call_json['responseStatus']
                phone_session.yafast_version = call2call_json['yAfastVersion']
                phone_session.verify_code = call2call_json['verifyCode']
                phone_session.caller_id = call2call_json['callerId']
                phone_session.calls_count = call2call_json['callsCount']
                phone_session.billing_per_call = call2call_json['bilingPerCall']
                phone_session.billing = call2call_json['biling']
                phone_session.errors = call2call_json['errors']
                db.session.add(phone_session)
                db.session.commit()

            else:
                error = True
                message = "something going wrong you can try again or send e-mail to cs@yemot.co.il."
            response_json = create_validation_response_json(message, error, data, status)
        except Exception as e:
            message = "something going wrong you can try again or send e-mail to cs@yemot.co.il" + str(e)
            error = True
            response_json = create_validation_response_json(message, error, data, status)

        return response_json
