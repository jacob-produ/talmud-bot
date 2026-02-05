import pandas as pd
from flask_restful import Resource
from school_manager.routes.auth import login_required
from flask import send_from_directory, request, send_file
from school_manager.constants.payment_check import OUTPUT_PAYMENT_FILE_PATH
from school_manager.modules.payment_check.payment_check_generator import PaymentCheckGenerator

class PaymentCheckGeneratorAPI(Resource):
    @login_required()
    def get(self):
        html_directory = '../assets/payment_check/html'
        return send_from_directory(html_directory, 'payment_check_index.html')

    @login_required()
    def post(self):
        file = request.files['fileUpload']

        if file.filename == '':
            return 'No selected file'
        if not file.filename.endswith(".xlsx") and not file.filename.endswith(".xls"):
            return "File type not supported"

        try:
            # Read the Excel file directly using pandas without saving it
            df = pd.read_excel(file)  # file is a file-like object

            PaymentCheckGenerator(df).generate()

            return send_file(OUTPUT_PAYMENT_FILE_PATH, as_attachment=True, download_name="payment_checks.pdf", mimetype='application/pdf')
        except Exception as e:
            return f"An error occurred: {e}"
