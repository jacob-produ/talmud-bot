import re
from flask import request
from flask_restful import Resource
from flask import request, jsonify
# from school_manager.models.validation_api_log import ValidationApiLog, create_logs_requests


# Creating the country codes and regex dictionary with English explanation
from school_manager.models import ValidationApiLog
from school_manager.routes.validation_bank_account import create_validation_response_json

country_regex_dictionary = {
    "US": ["[A-Za-z0-9]\d{8}$",
           "Begin with one letter or one digit [A-Za-z0-9], and follow by eight digits [d{8}$]"],
    # United-States, USA
    "GB": ["[A-Za-z0-9]\d{8}$",
           "Begin with one letter or one digit [A-Za-z0-9], and follow by eight digits [d{8}$]"],
    # United-Kingdom, Britain
    "UA": ["[A-Za-z0-9]{2}\d{6}$",
           "Begin with two letters or digits [A-Za-z0-9]{2}, and follow by six digits [d{6}$]"],
    # Ukraine
    "IT": ["[A-Za-z0-9]{2}\d{7}$",
           "Begin with two letters or digits [A-Za-z0-9]{2}, and follow by seven digits [d{7}$]"],
    # Italy
    "AR": ["[A-Za-z0-9]{3}\d{5}[Nn0-9]$",
           "Begin with three letters or digits [A-Za-z0-9]{3}, and follow by five digit [d{5}], end with 'N' "
           "/ n / digit [Nn0-9]$"],
    # Argentina
    "AT": ["[A-Za-z] *[A-Za-z0-9]{7,8}$",
           "begin with one letter [A-Za-z], and follow by optional space *, end with seven-eight letters or "
           "digits [A-Za-z0-9]{7}"],
    # Austria
    "BR": ["[A-Z]{2}\d{6}$",
           "Begin with two capital letters [A-Z]{2}, and follow by six digits [d{6}$]"],
    # Brazil
    "BG": ["\d{9}$", "Nine digits d{9}$"],
    # Bulgaria
    "DE": ["[CFGHJKLMNPRTVWXYZ][CFGHJKLMNPRTVWXYZ0-9]{8,10}$",
           "Begin with one letter from this options :[CFGHJKLMNPRTVWXYZ], follow by eight - ten letters or "
           "digits from this options: [CFGHJKLMNPRTVWXYZ0-9]{8,10}$"],
    # Germany
    "ES": ["[A-Za-z0-9]{2}[A-Za-z0-9]?\d{6}$",
           "Begin with two letters /digits [A-Za-z0-9]{2}, follow by one optional letter or digit [A-Za-z0-9]?,"
           " end with six digits [d{6}$]"],
    # Spain
    "GR": ["[A-Za-z]{2}\d{7}$", "Begin with two letters [A-Za-z]{2}, and follow by seven digits [d{7}$]"],
    # Greece
    "AU": ["[A-Za-z][A-Za-z]?\d{7}$",
           "Begin with one letter [A-Za-z], follow by one optional letter [A-Za-z]?, and end with seven "
           " digits [d{7}$]"],
    # Australia
    "FR": ["[0-9]{1,2}[A-Za-z]{2}\d{5}$",
           "Begin with two digits [d{2}], follow by two letters [A-Za-z]{2}, and end with five digits [d{5}$]"],
    # France
    "SE": ["\d{8}$", "Eight digits [d{8}$]"],
    # Sweden
    "RU": ["[0-9]{2} *-*[0-9]{2} *[0-9]{6}$",
           "Begin with two digits [0-9]{2}, follow by optional space and optional hyphen *-*, follow by two"
           " digits [0-9]{2}, follow by optional space *, and end with six digits [0-9]{6}$"],
    # Russian federation
    "MX": ["[A-Z0-9]\d{8,10}$", "Begin with one letter or digit [A-Z0-9], follow by eight-ten digits [{8,10}$]"],
    # Mexico
    "PL": ["[A-Za-z]{2}\d{7}$", "Begin with two letters [A-Za-z]{2}, follow by seven digits [d{7}$]"],
    # Poland
    "FI": ["[A-Za-z0-9]{2}\d{7,10}$",
           "Begin with two letters or digits [A-Za-z0-9]{2}, follow by seven-ten digits [d{7,10}$]"],
    # Finland
    "NZ": ["[A-Za-z]{2}\d{6}$", "Begin with two letters [A-Za-z]{2}, follow by six digits d{6}$"],
    # New Zealand
    "NL": ["[A-Za-z0-9]{8,9}$", "Eight or nine letters and digits [A-Za-z0-9]{8,9}$"],
    # Netherlands
    "CZ": ["\d{8}$", "Eight digits [d{8}$]"],
    # Czech
    "CH": ["[A-Za-z]\d{7,8}$", "Begin with one letter [A-Za-z], and follow by seven-eight digits [d{7,8}$]"],
    # Swiss, Switzerland
    "ZA": ["[AMam0-9]\d{8,12}$",
           "Begin with one letter or digit [A-Za-z0-9], follow by eight-Twelve digits [d{8,12}$]"],
    # South Africa
    "BE": ["[A-Za-z][A-Za-z0-9]\d{6,7}$",
           "Begin with one letter [A-Za-z], follow by one letter or digit [A-Za-z0-9],"
           " follow by six-seven digits d{6,7}$"],
    # Belgium
    "CA": ["[A-Za-z]{2}\d{6}$", "Begin with two letters [A-Za-z]{2}, follow by seven digits d{6}$"],
    # Canada
    "CL": ["[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-*[A-Za-z0-9]$",
           "Begin with one-two digits [0-9]{1,2}, follow by dot [\.], follow by three digits [0-9]{3}, "
           "follow by dot [\.], follow by three digits [0-9]{3}, follow by optional hyphen [-*], and end with "
           "one letter or digit [A-Za-z0-9]$"],
    # Chilean
}


class ValidationPassportAPI(Resource):
    def post(self):
        """
        handle data about the details of the passport number format, and make a validation test
        :return: Json answer [message: str, error: boolean, data: boolean]
        """
        # Creating default variables that will return in JSON
        error = False
        data = None
        status = "failed"

        try:
            # Example of what user_json get:
            # user_json = {'country_code': "US",
            #               'passport_id': "2548L6Gx",
            #               'api_password': 'fkhjas907412zxcl,nja7$%!%23!'}
            user_json = request.get_json()

            # Saving the values of specific key in a variable
            country_code = user_json['country_code']
            passport_id = user_json['passport_id']
            api_password = user_json['api_password']

            # Validation of the password and return if incorrect password
            if api_password != "fkhjas907412zxcl,nja7$%!#!":
                message = "The password is incorrect"
                error = True
                status = "failed"
                response_json = create_validation_response_json(message, error, data, status)
                return response_json
            else:
                # python check if key in dict using "in"
                if country_code not in country_regex_dictionary:
                    message = "Error, the key: " + country_code + " isn't exists in dictionary"
                    error = True
                    status = "failed"
                else:
                    # Create constant variables for the lists places
                    regex_index = 0
                    message_index = 1

                    result = passport_id_validation(passport_id, country_regex_dictionary[country_code][regex_index])
                    # regex index is the first index in the list of "country_code" in the "country regex dictionary"
                    # the regex passport number format

                    if result:
                        message = "Everything is found to be valid. The " + passport_id + " passport ID" \
                                  + " stand with the required legality: " \
                                  + country_regex_dictionary[country_code][message_index] + " for the country : " \
                                  + country_code

                        # message index is the second index in the list of "country_code" in the "country regex
                        # dictionary" the english message of the passport number format
                        data = True
                        status = "success"
                    else:
                        message = "Something going wrong. The " + passport_id + " passport ID" +\
                                  " NOT standing with the required legality: " \
                                  + country_regex_dictionary[country_code][message_index] + " for the country : " \
                                  + country_code,
                        # message index is the second index in the list of "country_code" in the "country regex
                        # dictionary" the english message of the passport number format
                        error = False
                        data = False
                        status = "failed"

            response_json = create_validation_response_json(message, error, data, status)
            jsonify(ValidationApiLog.create_logs_requests(response_json, user_json, "passport number format"))
        except Exception as e:
            print("Exception occurred for value: " + repr(e))
            message = "Invalid input, Error message: " + str(e)
            error = True
            status = "failed"
            response_json = create_validation_response_json(message, error, data, status)
        return response_json


def passport_id_validation(passport_id, country_regex):
    """
    The validation function for regex passport number format
    :type passport_id: str
    :type country_regex: str
    :rtype: bool
    """
    country_regex = str(country_regex)
    pattern = re.compile(r'{}'.format(country_regex))
    answer = pattern.match(passport_id)
    if answer is None:
        print('The regex of country : ' + country_regex)
        return False
    else:
        return True
