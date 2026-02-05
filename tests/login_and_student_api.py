import requests

json_login = {
    "username": "external_api_user", "password": "t43GSF0At@T9lRnd*ZWXtS%iU%77Maa4Ic5mEhl", "remember_me": True
}

json_student = {
    "first_name": "ליאורה", "identity": "312613623", "identity_type": "תעודת זהות", "last_name": "כהן",
    "birth_date": "1993-12-09T00:00:00", "main_phone_number": "", "secondary_phone_number": "", "state": "", "city": "",
    "street": "", "street_number": "", "active": "False", "deleted": "False", "marital_status": "",
    "first_parent_phone": "", "second_parent_phone": "", "mail": "", "father_name": "", "partner_name": "",
    "language": "", "entrance_country_date": "2020-11-09T00:00:00", "departure_country_date": "2021-11-09T00:00:00",
    "service_status": ""
}

json_update_student = {
    "birth_date": "1997-11-09T00:00:00", "first_name": "ליאור", "identity": "539316204", "identity_type": "דרכון",
    "last_name": "לוי", "deleted": "True"
}

try:
    # Requests api LOGIN and api STUDENT (read, create, update, delete)
    session = requests.session()
    requests_post_login = session.post('https://schoolmanager.services//auth/login',
                                       json=json_login)
    cookies = requests_post_login.cookies
    requests_get_read_student = requests.get('https://schoolmanager.services/student/17',
                                             cookies=cookies)
    requests_post_create_student = requests.post('https://schoolmanager.services/student',
                                                 cookies=cookies, json=json_student)
    requests_put_update_student = requests.put('https://schoolmanager.services/student/543',
                                               json=json_update_student, cookies=cookies)
    requests_delete_delete_student = requests.delete('https://schoolmanager.services/student/542', cookies=cookies)

    # Saving the responses in JSON format
    json_response_delete_student = requests_delete_delete_student.json()
    json_response_update_student = requests_put_update_student.json()
    json_response_create_student = requests_post_create_student.json()
    json_response_read_student = requests_get_read_student.json()
    json_response_login = requests_post_login.json()

    # Printing the responses in JSON format
    print("---------LOGIN---------")
    print(json_response_login)
    print("---------READ---------")
    print(json_response_read_student)
    print("---------CREATE---------")
    print(json_response_create_student)
    print("---------UPDATE---------")
    print(json_response_update_student)
    print("---------DELETE---------")
    print(json_response_delete_student)


except Exception as e:
    print("Exception occurred for value: " + repr(e))
