import re

import pdfkit, io, os, random, requests, uuid

from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.generated_form import GeneratedForm
from school_manager.models.form_template import FormTemplate
from school_manager.models.committee_member import CommitteeMember
from school_manager.models.institution import Institution
from school_manager.models.branch import Branch
from school_manager.models.student import Student

# from DB import Forms, ComitteeMembers, Institution

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'pdf_files')
HTML_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'html_templates')

# Make sure that pdf_files folder is existed. If not, create it

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


class PDFGenerator(object):

    def __init__(self, wkhtmltopdf_path, output_dir=OUTPUT_DIR):
        self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        self.pdfkit_options = {
            "enable-local-file-access": ''
        }
        self.output_dir = output_dir

        self.course_enrollment = None
        self.student = None

        self.branch = None
        self.institution = None

        self.committee_member = None

    def get_student_attributes(self, course_enrollment_id):
        # extract course_enrollment using student_course_enrollment_id
        course_enrollment = CourseEnrollment.read(id=course_enrollment_id, many=False)

        # fetch student
        student_id = course_enrollment.get('fk_student_id')
        student = Student.read(id=student_id, many=False)
        return course_enrollment, student

    def get_institution_attributes(self, course_enrollment):
        # use branch to get related institution and committee-member (using institution id)
        branch_id = course_enrollment.get('fk_branch_id')
        branch = Branch.read(id=branch_id, many=False)

        institution_id = branch.get('fk_institution_id')
        institution = Institution.read(id=institution_id, many=False)

        return branch, institution

    # TODO: check case when there are more than one committee for institution
    def get_committee_attributes(self, institution):
        committee_member = CommitteeMember.read(fk_institution_id=institution.get('id'), many=False)
        return committee_member

    def set_static_attributes(self, course_enrollment_id):
        self.course_enrollment, self.student = self.get_student_attributes(course_enrollment_id)
        self.branch, self.institution = self.get_institution_attributes(self.course_enrollment)
        self.committee_member = self.get_committee_attributes(self.institution)

    def set_dynamic_attributes(self, **kwargs):
        raise NotImplementedError()

    def get_static_attributes(self):
        student = {f'student_{k}': v for k, v in self.student.items()}
        institution = {f'institution_{k}': v for k, v in self.institution.items()}
        committee_member = {f'committee_member_{k}': v for k, v in self.committee_member.items()}
        course_enrollment = {f'course_enrollment_{k}': v for k, v in self.course_enrollment.items()}
        return {**committee_member, **institution, **student, **course_enrollment}

    def get_dynamic_attributes(self):
        raise NotImplementedError()

    def get_form_template_keys(self):
        raise NotImplementedError()

    def update_html_form(self, form_id):
        form_data = FormTemplate.read(id=form_id, many=False)
        form_name, form_template_path = form_data.get('name'), form_data.get('template_path')
        form_template_path = os.path.join(HTML_TEMPLATE_PATH, form_template_path)

        static_attributes, dynamic_attributes = self.get_static_attributes(), self.get_dynamic_attributes()
        all_attributes = {**static_attributes, **dynamic_attributes}

        with open(form_template_path, 'r', encoding="utf8") as in_file:
            html_str = in_file.read()

        # form_keys = self.get_form_template_keys()

        def get_keys_from_html(html_str):
            keys = re.findall(r'{(.*?)}', html_str)
            return keys

        form_keys = get_keys_from_html(html_str)
        print(all_attributes)

        for att_name in form_keys:
            att_value = all_attributes.get(att_name, '')
            if att_value == "":
                att_value = all_attributes.get("form_" + str(att_name), '')
            if "date" in att_name:
                att_value = att_value[:10]
            print(att_value)
            print(att_name)
            html_str = html_str.replace("{" + att_name + "}", str(att_value))
        return html_str

    def convert_html_to_pdf(self, html_str, output_file_path):
        pdfkit.from_string(html_str, output_file_path, configuration=self.pdfkit_config, options=self.pdfkit_options)

        # read the PDF file
        pdf_data = io.BytesIO()
        with open(output_file_path, 'rb') as fo:
            pdf_data.write(fo.read())
            pdf_data.seek(0)
        return pdf_data

    def create_form(self, form_id, course_enrollment_id, **kwargs):
        output_file_path = os.path.join(self.output_dir, f'{str(uuid.uuid4())}.pdf')

        self.set_static_attributes(course_enrollment_id)
        self.set_dynamic_attributes(**kwargs)

        html_str = self.update_html_form(form_id)
        pdf_io = self.convert_html_to_pdf(html_str, output_file_path)
        return pdf_io

    @classmethod
    def get_form_pdf_generator_by_id(cls, form_id):
        from school_manager.modules.form_generator.property_tax_pdf_generator import PropertyTaxPDFGenerator
        from school_manager.modules.form_generator.student_approval_pdf_generator import StudentsApprovalPDFGenerator
        from school_manager.modules.form_generator.student_special_approval_pdf_generator import \
            StudentsSpecialApprovalPDFGenerator
        from school_manager.modules.form_generator.social_services_form_pdf_generator import SocialServicesPDFGenerator

        forms = FormTemplate.get_all_forms_dict()

        if form_id not in forms:
            raise NotImplementedError()
        elif forms[form_id]['name'].lower().strip() == 'property_tax':
            return PropertyTaxPDFGenerator()
        elif forms[form_id]['name'].lower().strip() == 'student_approval':
            return StudentsApprovalPDFGenerator()
        elif forms[form_id]['name'].lower().strip() == 'student_special_approval':
            return StudentsSpecialApprovalPDFGenerator()
        elif forms[form_id]['name'].lower().strip() == 'social_service':
            return SocialServicesPDFGenerator()


if __name__ == '__main__':
    pass
