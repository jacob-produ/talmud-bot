from school_manager.models.student import Student
from school_manager.models.course_enrollment import CourseEnrollment
from datetime import datetime
from flask import request
from flask_restful import Resource


class ValidationLocalPhoneNumber(Resource):
    def get(self):
        id_list_message = 0
        try:
            # Get the phone number from the GET request
            api_phone_value = request.args.get(list(request.values.keys())[0])

            #  Get the id of the student that the main phone number is phone number for check
            res_student = Student.read(many=False, main_phone_number=api_phone_value)['id']

            #  Get the rows of the student courses that the main phone number is phone number for check
            course_all_rows = CourseEnrollment.read(many=True, fk_student_id=res_student)

            #  Saving the today date, start and end date of the course of the student in list
            today = datetime.now()
            today_list = today.strftime("%Y-%m-%d %H:%M:%S")
            today_datetime = datetime.strptime(today_list, '%Y-%m-%d %H:%M:%S')

            for course in course_all_rows:
                if course['start_date'] is None: course['start_date'] = '9999-12-31T23:59:59'
                if course['end_date'] is None: course['end_date'] = '9999-12-31T23:59:59'

                start_date_datetime = datetime.strptime(course['start_date'], '%Y-%m-%dT%H:%M:%S')
                end_date_datetime = datetime.strptime(course['end_date'], '%Y-%m-%dT%H:%M:%S')

                #  Condition if the student is in active course
                if start_date_datetime.date() < today_datetime.date() < end_date_datetime.date():
                    id_list_message = 1
                    break
                else: id_list_message = 3

        except Exception as e:
            id_list_message = 2

        return id_list_message
