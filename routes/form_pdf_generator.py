from flask import send_file, request
from flask_restful import Resource

from school_manager.modules.form_generator.pdf_generator import PDFGenerator


class FormPDFGenerator(Resource):

    @staticmethod
    def post():
        # extract arguments
        kwargs = request.get_json()
        form_id = kwargs['form_id']
        course_enrollment_id = int(kwargs['course_enrollment_id'])

        kwargs.pop("form_id")
        kwargs.pop("course_enrollment_id")

        # build PDF form and save to locally
        generator = PDFGenerator.get_form_pdf_generator_by_id(form_id)
        file_bytes = generator.create_form(form_id, course_enrollment_id, **kwargs)

        # response with the locally generated file as a file to download
        return send_file(file_bytes, mimetype='application/pdf',
                         attachment_filename=f'form.pdf')