from school_manager.db import db
from school_manager.models.crud_mixin import BaseMixin
from flask import request
import datetime


class ValidationApiLog(BaseMixin, db.Base):
    __tablename__ = "validation api log"
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(30), nullable=False)  # The api name, validation bank account or passport number
    verified_code = db.Column(db.String(5), nullable=False)  # country / bank code
    verified_string = db.Column(db.String(30), nullable=False)  # passport / bank,branch number
    error = db.Column(db.Boolean(), nullable=False)
    result = db.Column(db.Boolean(), nullable=True)  # Acceptable or Not acceptable
    message = db.Column(db.String(350), nullable=False)  # The message answered
    user_agent = db.Column(db.String(450), nullable=False)  # Source user agent
    ip_address = db.Column(db.String(15), nullable=False)  # Source ip address
    time = db.Column(db.String(25), nullable=False)  # Time call to API

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,
                                {i: self.__dict__[i] for i in self.__dict__ if i != "_sa_instance_state"})

    @classmethod
    def create_logs_requests(cls, answer_json, user_json, name_api):
        # Create a ValidationApiLog Class
        validation_api_log = ValidationApiLog()

        # get the user agent and the ip address
        user_agent = request.user_agent
        ip_address = request.remote_addr

        # Saving the values of specific key in a variable
        if name_api == "passport number format":
            the_code = user_json['country_code']
            the_id = user_json['passport_id']
        elif name_api == "bank account":
            bank_inspection = user_json['bank_inspection']
            the_code = bank_inspection["Bank"]

            # branch_number = bank_inspection["Snif"], account_number = bank_inspection["Account"]
            the_id = str(bank_inspection["Account"]) + ',' + str(bank_inspection["Snif"])

        # Create a Log row
        validation_api_log.api_name = name_api
        validation_api_log.verified_code = str(the_code)
        validation_api_log.verified_string = the_id
        validation_api_log.error = answer_json['error']
        validation_api_log.result = answer_json['data']
        validation_api_log.message = answer_json['message']
        validation_api_log.user_agent = str(user_agent)
        validation_api_log.ip_address = ip_address
        validation_api_log.time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')

        object_data = validation_api_log.__dict__  # Create dict from all the class
        del object_data['_sa_instance_state']  # Delete the first key-value pair in the dictionary

        # Add and commit the log row to the db using create/crud_mixin function
        ValidationApiLog.create(object_data)
        print("Test Log of API was successfully done")
