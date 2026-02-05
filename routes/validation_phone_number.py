from flask import request
from flask_restful import Resource
import requests
from bs4 import BeautifulSoup


class ValidationPhoneNumberAPI(Resource):
    def get(self):
        """
        handle data about the details of the phone number list, and make a validation test if exist
        :return: String "OK" / "NOT"
        """
        try:
            # Saving the key as sent
            api_key = list(request.values.keys())[0]

            # Check if the Key is correct and return error message if not
            if list(request.values.keys())[0].upper() == "APIPHONE":
                print(True)
            else:
                return "Error: The Params Key is not exist, please try again or contact with the Admin"

            # Example of what phone_number get: http://192.168.1.127/phone_number_validation?APIPHONE=123456
            # Saving the values of specific key in a variable
            api_phone_value = request.args.get(api_key)

            # Saving the link with the phone number to check
            api_phone_link = "https://script.google.com/macros/s" \
                             "/AKfycbz8LyVdazdHotnJH428Q3ULT3yVW6PZ8evyO5A3_3k3DOj0s6cuI8tLZYVadi0eMnErHA/exec?action" \
                             "=GetPhoneStatus&APIPHONE=" + api_phone_value

            # Making a get request
            response = requests.get(api_phone_link)

            # Saving the url that back from Google script
            result_response = requests.get(
                url=response.url.__str__()
            )

            # Saving the content into variable using Beautiful soup
            phone_response = BeautifulSoup(result_response.content, 'html.parser')
        except Exception as e:
            print("Exception occurred for value: " + repr(e))
            answer_string = "Invalid input, Error message: " + str(e)
            return answer_string
        return phone_response.string
