import os
from school_manager.modules.form_generator.pdf_generator import PDFGenerator

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_files')
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


class PropertyTaxPDFGenerator(PDFGenerator):

    def __init__(self, wkhtmltopdf_path=WKHTMLTOPDF_PATH, output_dir=OUTPUT_DIR):
        super().__init__(wkhtmltopdf_path, output_dir)

        self.form_payment_amount = None
        self.form_approval_period = None
        self.form_generation_date = None

    def set_dynamic_attributes(self, **kwargs):
        self.form_payment_amount = kwargs.get('form_payment_amount')
        self.form_approval_period = kwargs.get('form_approval_period')
        self.form_generation_date = kwargs.get('form_generation_date')

    def get_dynamic_attributes(self):
        return dict(form_payment_amount=self.form_payment_amount,
                    form_approval_period=self.form_approval_period,
                    form_generation_date=self.form_generation_date)

    def get_form_template_keys(self):
        return ['form_generation_date', 'student_first_name',
                'student_last_name', 'student_identity',
                'form_payment_amount', 'form_approval_period',
                'committee_member_first_name', 'committee_member_last_name',
                'committee_member_identity']

if __name__ == '__main__':
    os.environ['WKHTMLTOPDF_LOCATION'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\bin\\wkhtmltopdf.exe"
    os.environ['PDF_OUTPUT_DIR'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\output"
    os.environ['HTML_TEMPLATE_DIR'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\HtmlTemplates"


    wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin'

    pdfgen = PropertyTaxPDFGenerator(wkhtmltopdf_path)

    args = {
        "student_first_name": "אלי",
        "student_last_name": "כהן",
        "student_identity_type": "תעודת זהות",
        "student_identity": 123456,
        "student_birth_date": "1/9/1955",
        "student_gender": "גבר",
        "student_marital_status": "נשוי",
        "student_birth_state": "ישראל",
        "student_month_since_registration": 14,
        "student_study_type_name": "יום שלם",
        "student_study_type_id": 600,
        "student_active_status": "לומד/פעיל",

        "institution_name": "הדר יוסף",
        "institution_id": "01",

        "report_month": "12/2021",

        "generated_report_reporter_full_name": "חיים חורי",
        "generated_report_report_date": "20/01/2021",
        "committee_member_role": "מנהל כללי"
    }
    # pdfgen.generate_and_delete('1', 'student-approval-form-new', args)
    pdfgen.generate_and_delete('1', 'index', args, remove_tmp_file=False)