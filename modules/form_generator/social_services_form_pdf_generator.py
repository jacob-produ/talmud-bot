import os
from school_manager.modules.form_generator.pdf_generator import PDFGenerator

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_files')
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


class SocialServicesPDFGenerator(PDFGenerator):

    def __init__(self, wkhtmltopdf_path=WKHTMLTOPDF_PATH, output_dir=OUTPUT_DIR):
        super().__init__(wkhtmltopdf_path, output_dir)
        self.form_generation_date = None
        self.form_part_of_the_day = None
        self.form_hours_of_study = None
        self.form_month_of_study = None
        self.form_amount_of_money_for_scholarship = None

    def set_dynamic_attributes(self, **kwargs):
        self.form_generation_date = kwargs.get('form_generation_date')
        self.form_part_of_the_day = kwargs.get('form_part_of_the_day')
        self.form_hours_of_study = kwargs.get('form_hours_of_study')
        self.form_month_of_study = kwargs.get('form_month_of_study')
        self.form_amount_of_money_for_scholarship = kwargs.get('form_amount_of_money_for_scholarship')

    def get_dynamic_attributes(self):
        return dict(form_generation_date=self.form_generation_date, form_part_of_the_day=self.form_part_of_the_day,
                    form_hours_of_study=self.form_hours_of_study, form_month_of_study=self.form_month_of_study,
                    form_amount_of_money_for_scholarship=self.form_amount_of_money_for_scholarship)

    def get_form_template_keys(self):
        return ['institution_short_name', 'institution_city',
                'institution_phone_number', 'institution_identity',
                'student_first_name', 'student_last_name', 'student_identity',
                'institution_short_name', 'course_enrollment_start_date',
                'part_of_the_day', 'hours_of_study', 'month_of_study', 'amount_of_money_for_scholarship'
                                                                       'committee_member_first_name',
                'committee_member_last_name', 'committee_member_role',
                'generated_form_date']
