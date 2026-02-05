from flask import send_file, request
from flask_restful import Resource, reqparse

from school_manager.modules.FormGenerator.PdfGenerator import PdfGenerator


class PdfGeneratorResource(Resource):
    def __init__(self):
        pass

    def post(self):

        # extract arguments
        student_course_registration_id = int(request.args['student_course_registration_id'])
        form_id = request.args['form_id']
        args_dict = request.get_json()  # args['args_dict']

        # build PDF form and save to locally
        generator = PdfGenerator()
        file_bytes = generator.generate_and_delete(student_course_registration_id, form_id, args_dict)

        # response with the locally generated file as a file to download
        return send_file(file_bytes, mimetype='application/pdf',
                         attachment_filename=f'form.pdf')
