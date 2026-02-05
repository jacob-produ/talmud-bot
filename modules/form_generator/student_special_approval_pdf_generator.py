import os
from school_manager.modules.form_generator.pdf_generator import PDFGenerator

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_files')
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


class StudentsSpecialApprovalPDFGenerator(PDFGenerator):

    def __init__(self, wkhtmltopdf_path=WKHTMLTOPDF_PATH, output_dir=OUTPUT_DIR):
        super().__init__(wkhtmltopdf_path, output_dir)

        self.form_student_gender = None
        self.form_student_month_since_registration = None
        self.form_student_study_type_name = None
        self.form_report_month = None
        self.form_generation_date = None

    def set_dynamic_attributes(self, **kwargs):
        self.form_student_gender = kwargs.get('form_student_gender')
        self.form_student_month_since_registration = kwargs.get('form_student_month_since_registration')
        self.form_student_study_type_name = kwargs.get('form_student_study_type_name')
        self.form_report_month = kwargs.get('form_report_month')
        self.form_generation_date = kwargs.get('form_generation_date')

    def get_dynamic_attributes(self):
        return dict(form_student_gender=self.form_student_gender,
                    form_student_month_since_registration=self.form_student_month_since_registration,
                    form_student_study_type_name=self.form_student_study_type_name,
                    form_report_month=self.form_report_month,
                    form_generation_date=self.form_generation_date)

    def get_form_template_keys(self):
        return ['form_generation_date', 'student_first_name', 'student_last_name', 'student_identity_type', 'student_identity',
                'student_birth_date', 'student_gender',
                'student_marital_status', 'student_state', 'student_active',
                'student_month_since_registration',
                'institution_name', 'institution_id',
                'student_study_type_name',
                'course_enrollment_course_type', 'course_enrollment_course_type',
                'report_month',
                'generated_report_reporter_full_name']
