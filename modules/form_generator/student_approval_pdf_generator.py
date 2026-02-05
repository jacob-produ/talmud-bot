import os
from school_manager.modules.form_generator.pdf_generator import PDFGenerator

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_files')
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'


class StudentsApprovalPDFGenerator(PDFGenerator):

    def __init__(self, wkhtmltopdf_path=WKHTMLTOPDF_PATH, output_dir=OUTPUT_DIR):
        super().__init__(wkhtmltopdf_path, output_dir)
        self.form_generation_date = None
        pass

    def set_dynamic_attributes(self, **kwargs):
        self.form_generation_date = kwargs.get('form_generation_date')

    def get_dynamic_attributes(self):
        return dict(form_generation_date=self.form_generation_date)

    def get_form_template_keys(self):
        return ['form_generation_date', 'student_first_name',
                'student_last_name', 'student_identity',
                'committee_member_first_name', 'committee_member_last_name', 'committee_member_identity']

# if __name__=='__main__':
