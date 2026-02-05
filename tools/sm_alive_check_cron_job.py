import sys
from datetime import datetime
import time
from time import sleep
import requests
import smtplib
import os
import logging
import os.path


def list_of_running_services():
    try:
        # Restart for school manager service
        os.popen("systemctl restart school_manager_server")
    except OSError as ose:
        # Add a log into the log.txt file [print("Error while running the command", ose)]
        logging.debug("Error while running the command", ose)
    pass

def email_sending():
    try:
        server = smtplib.SMTP('smtp.outlook.com', 587)
        server.starttls()
        server.login('Fensive@outlook.com', 'F3n5iv3t35tin6')
        server.sendmail('SM-Alive checker <Fensive@outlook.com>', 'Fensive@outlook.com',
                        'Subject: SMTP SM-Alive checker'
                        'message \n\n This is e-mail from python. The service school manager was unavailable')
        server.quit()
        logging.debug("Mail sent...")
    except Exception as e:
        logging.debug("Failed to send email message: " + str(e))


# Log target file and message level (all levels: critical, error, warning, info, debug)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename="/root/log.txt", level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')

# Add a log into the log.txt file
logging.debug("Testing if the service alive...")
sys.stdout.flush()

# File to check
file_path = r'/root/log.txt'

# Get the size (bytes)
size_of_log_txt_file = os.path.getsize(file_path)

# Remove the 5,000 firsts rows (60 bytes in average per row, remove 300,000 bytes)
# if the file is bigger than 1mb = 1,048,576 bytes
if size_of_log_txt_file > 1048576:
    with open('/root/log.txt', 'r') as log:
        data = log.read().splitlines(True)
    with open('/root/log.txt', 'w') as old_log:
        old_log.writelines(data[5000:])

# Creating JSON response with wrong password
json_wrong_password = {
    "country_code": "GB",
    "passport_id": "123456789",
    "api_password": "fkhjas907412zxcl,nja7$%!#!3"
}

try:
    # Post requests for passport validation API with the JSON wrong password every 30 seconds
    requests_post = requests.post('https://schoolmanager.services/passport_id_validation',
                                  json=json_wrong_password,
                                  verify=False,
                                  timeout=60)

    # Saving the response in JSON format
    json_response = requests_post.json()

except Exception as e:
    # Add a log into the log.txt file [print("Exception occurred for value: " + repr(e))]
    logging.debug("Exception occurred for value: " + repr(e))
    sys.stdout.flush()
    json_response = {'message': repr(e),
                     'error': False,
                     'data': False,
                     'status': 'Not uses'}

# Expectation for JSON response when the password is incorrect
json_response_expectation = {'message': 'The password is incorrect',
                             'error': True,
                             'data': None,
                             'status': 'Not uses'}

# Checking if the response stand with the expectation, if not sending E-mail that the service unavailable
if json_response['message'] == json_response_expectation['message']:
    # Add a log into the log.txt file [print("The service is available")]
    logging.debug("The service is available")
    sys.stdout.flush()
else:
    # Add a log into the log.txt file [print("The service is unavailable - Email sent to administrator")]
    logging.debug("The service is unavailable")
    sys.stdout.flush()
    list_of_running_services()
    email_sending()
    logging.debug("Email Sent and Service Restart Done")
