import pdfkit
import io
import os
import random
import requests

from school_manager.models.course_enrollment import CourseEnrollment
from school_manager.models.generated_form import GeneratedForm
from school_manager.models.form_template import FormTemplate
from school_manager.models.committee_member import CommitteeMember
from school_manager.models.institution import Institution
from school_manager.models.branch import Branch
from school_manager.models.student import Student

# from DB import Forms, ComitteeMembers, Institution


class PdfGenerator(object):

    def __init__(self):
        self.config = pdfkit.configuration(wkhtmltopdf=os.environ.get('WKHTMLTOPDF_LOCATION'))
        self.output_dir = os.environ.get('PDF_OUTPUT_DIR')

    def generate_and_delete(self, student_course_enrollment_id, form_id, args_dict, remove_tmp_file=True):

        # extract course_enrollment using student_course_enrollment_id
        course_enrollment = CourseEnrollment.read(id=student_course_enrollment_id, many=False)

        # fetch student
        student_id = course_enrollment.get('fk_student_id')
        student = Student.read(id=student_id, many=False)

        # use branch to get related institution and committee-member (using institution id)
        branch_id = course_enrollment.get('fk_branch_id')
        branch = Branch.read(id=branch_id, many=False)
        institution_id = branch.get('fk_institution_id')

        institution = Institution.read(id=institution_id, many=False)
        committee_member = CommitteeMember.read(fk_institution_id=institution_id, many=False)

        # adding prefix to each key for easier identification and clear meaning
        student = {f'student_{k}': v for k, v in student.items()}
        institution = {f'institution_{k}': v for k, v in institution.items()}
        committee_member = {f'committee_member_{k}': v for k, v in committee_member.items()}
        course_enrollment = {f'course_enrollment_{k}': v for k, v in course_enrollment.items()}
        form_args = {**args_dict, **committee_member, **institution, **student, **course_enrollment}

        # create an unique output filename (to avoid problems while there are multiple requests in parallel)
        rand = random.random()
        tmp_output_file = f'{self.output_dir}/out_{rand}.pdf'

        # read HTML into as string
        form_path = f"modules/FormGenerator/html_templates/{form_id}.html"
        with open(form_path, 'r', encoding="utf8") as in_file:
            html_str = in_file.read()

        '''
        in case we want to read the template files from a URL 
        (which is defined in the form_template table in the DB):
        
        form = FormTemplate.read(name=form_id, many=False)
        form_url = form.get('template_path')
        html_str = requests.get(form_url).text
        '''

        # add form values
        for k, v in form_args.items():
            if v and "date" in k:
                v = v[:10]
            html_str = html_str.replace("{"+k+"}", str(v))

        # generate the PDF
        options = {
            "enable-local-file-access": ''
        }
        pdfkit.from_string(html_str, tmp_output_file, configuration=self.config, options=options)

        # read the PDF file
        return_data = io.BytesIO()
        with open(tmp_output_file, 'rb') as fo:
            return_data.write(fo.read())
            return_data.seek(0)

        # remove the generated PDF file
        if remove_tmp_file:
            os.remove(tmp_output_file)

        return return_data


if __name__ == '__main__':
    os.environ['WKHTMLTOPDF_LOCATION'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\bin\\wkhtmltopdf.exe"
    os.environ['PDF_OUTPUT_DIR'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\output"
    os.environ['HTML_TEMPLATE_DIR'] = "C:\\Users\\Gal\\PycharmProjects\\SchoolManagement\\HtmlTemplates"

    pdfgen = PdfGenerator()

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
