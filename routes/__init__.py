from . import auth
from . import auth_student
from .user import UserAPI
from .exam import ExamAPI
from .loan import LoanAPI
from .get_opt import GetOpt
from .index import IndexAPI
from flask_restful import Api
from .branch import BranchAPI
from .income import IncomeAPI
from .talmud import TalmudAPI, TalmudProgressAPI, TalmudDownloadAPI
from .msv import MSVExpenseAPI
from .expense import ExpenseAPI
from .student import StudentAPI
from .invoice import InvoiceAPI
from .donator import DonatorAPI
from .employee import EmployeeAPI
from .examiner import ExaminerAPI
from .supplier import SupplierAPI
from .clearing import ClearingAPI
from .raw_table import RawTableAPI
from .check import CheckExpenseAPI
from .institution import InstitutionAPI
from .finance_card import FinanceCardAPI
from .bank_account import BankAccountAPI
from .msv_scraping import MSVScrapingAPI
from .expense_draft import ExpenseDraftAPI
from .general_lists import GeneralListsAPI
from .income_source import IncomeSourceAPI
from .link_current_account import LinkCAAPI
from .student_income import StudentIncomeAPI
from .finance_report import FinanceReportAPI
from .payment_basket import PaymentBasketAPI
from .hello_world_api import HelloWorldApiTest
from .current_account import CurrentAccountAPI
from .payment_failure import PaymentFailureAPI
from .form_pdf_generator import FormPDFGenerator
from .reception_basket import ReceptionBasketAPI
from .course_enrollment import CourseEnrollmentAPI
from .clearing_platform import ClearingPlatformAPI
from .trend_coordinator import TrendCoordinatorAPI
from .student_insurance import StudentInsuranceAPI
from .download_template import DownloadTemplateAPI
from .periodic_reception import PeriodicReceptionAPI
from .PdfGeneratorResource import PdfGeneratorResource
from .clearing_validation import ClearingValidationAPI
from .transactions_report import TransactionsReportAPI
from .general_bank_account import GeneralBankAccountAPI
from .validation_bank_account import ValidationAccountAPI
from .FormAttributesResource import FormAttributesResource
from .read_student_auth_student import StudentAuthByOtpAPI
from .finance_report_filters import FinanceReportFiltersAPI
from .payment_check_generator import PaymentCheckGeneratorAPI
from .validation_phone_number import ValidationPhoneNumberAPI
from .reception_basket_filters import ReceptionBasketFiltersAPI
from .institution_bank_account import InstitutionBankAccountAPI
from .periodic_reception_report import PeriodicReceptionReportAPI
from .validation_country_passport_id import ValidationPassportAPI
from .periodic_reception_filters import PeriodicReceptionFiltersAPI
from .validation_local_phone_number import ValidationLocalPhoneNumber
from .transactions_report_filters import TransactionsReportFiltersAPI
from .institution_branch_coordinator import InstitutionBranchCoordinatorAPI
from .course_enrollment_trend_coordinator_attribution import CourseEnrollmentTrendCoordinatorAttributionAPI


def init_app(app):
    # Create restful api object
    api = Api(app)

    # Register the auth blueprint
    app.register_blueprint(auth.bp)

    # Create restful app object
    app_student = app

    # Register the auth blueprint
    app_student.register_blueprint(auth_student.bp_student)


    # Register the index route
    api.add_resource(IndexAPI, '/')

    # Bank Account route
    api.add_resource(BankAccountAPI, '/bank_account', '/bank_account/<string:bank_account_id>')

    # Branch route
    api.add_resource(BranchAPI, '/branch', '/branch/<string:branch_id>', '/branch/csv_template')

    # Employee route
    api.add_resource(EmployeeAPI, '/employee', '/employee/<string:employee_id>')

    # Exam route
    api.add_resource(ExamAPI, '/exam', '/exam/<string:exam_id>')

    # Examiner route
    api.add_resource(ExaminerAPI, '/examiner', '/examiner/<string:examiner_id>')

    # Expense route
    api.add_resource(ExpenseAPI, '/expense', '/expense/print_payment', '/expense/<string:expense_id>',
                     '/expense/merge_payment', '/expense/split_payment',
                     '/expense/current_account/<int:current_account_id>')

    # Income route
    api.add_resource(IncomeAPI, '/income', '/income/<string:income_id>', '/income/csv_template',
                     '/income/print_payment', '/income/merge_payment', '/income/split_payment',
                     '/income/current_account/<int:current_account_id>')

    # Income Source route
    api.add_resource(IncomeSourceAPI, '/income_source', '/income_source/<string:income_source_id>')

    # Institution Source route
    api.add_resource(InstitutionAPI, '/institution', '/institution/<string:institution_id>')

    # Loan Source route
    api.add_resource(LoanAPI, '/loan', '/loan/<string:loan_id>')

    # Student Source route
    api.add_resource(StudentAPI, '/student', '/student/<string:student_id>', '/student/csv_template')

    # Student Source route
    api.add_resource(StudentAuthByOtpAPI, '/read_student_auth_student', '/read_student_auth_student/<string:student_id>', '/read_student_auth_student/csv_template')

    # Course Enrollment Source route
    api.add_resource(CourseEnrollmentAPI, '/course_enrollment', '/course_enrollment/csv_template')

    # Course Enrollment Trend Attribution Source route
    api.add_resource(CourseEnrollmentTrendCoordinatorAttributionAPI, '/course_enrollment_trend_coordinator_attribution',
                     '/course_enrollment_trend_coordinator_attribution/<string:trend_attribution_id>',
                     '/course_enrollment_trend_coordinator_attribution/csv_template',
                     '/course_enrollment_trend_coordinator_attribution/student/<string:student_id>', )

    # Supplier Source route
    api.add_resource(SupplierAPI, '/supplier', '/supplier/<string:supplier_id>', '/supplier/csv_template')

    # Trend Coordinator Source route
    api.add_resource(TrendCoordinatorAPI, '/trend_coordinator', '/trend_coordinator/<string:trend_coordinator_id>',
                     '/trend_coordinator/csv_template')

    # User Route
    api.add_resource(UserAPI, '/user', '/user/<string:user_id>')

    # Current Account Route
    api.add_resource(CurrentAccountAPI, '/current_account', '/current_account/<string:current_account_id>',
                     '/current_account/csv_template')

    api.add_resource(FinanceReportAPI, '/finance_report', '/finance_report/export',
                     '/finance_report/<string:attribution>/<string:attribution_id>')

    api.add_resource(FinanceReportFiltersAPI, '/finance_report/filters')

    api.add_resource(FinanceCardAPI, '/finance_card/<string:attribution>/<string:attribution_id>')

    api.add_resource(PaymentBasketAPI, '/payment_basket')

    api.add_resource(TransactionsReportAPI, '/transactions_report')

    api.add_resource(TransactionsReportFiltersAPI, '/transactions_report/filters')

    api.add_resource(InstitutionBranchCoordinatorAPI, '/institution_branch_coordinator')

    api.add_resource(LinkCAAPI, '/link_ca/', '/link_ca/<string:link_type>', '/link_ca/associated/<int:ca_id>')

    api.add_resource(ClearingAPI, '/clearing', '/clearing/csv_template')

    api.add_resource(ClearingPlatformAPI, '/clearing_platform', '/clearing_platform/<int:platform_id>',
                     '/clearing_platform/csv_template')

    api.add_resource(ClearingValidationAPI, '/clearing_validation', '/clearing_validation/csv_template')

    api.add_resource(MSVExpenseAPI, '/msv', '/msv/csv_template')

    api.add_resource(CheckExpenseAPI, '/check', '/check/csv_template')

    api.add_resource(InvoiceAPI, '/invoice')

    api.add_resource(StudentInsuranceAPI, '/student_insurance', '/student_insurance/csv_template')

    api.add_resource(ExpenseDraftAPI, '/expense_draft', '/expense_draft/csv_template')

    api.add_resource(DonatorAPI, '/donator', '/donator/<int:donator_id>', '/donator/csv_template')

    api.add_resource(PeriodicReceptionAPI, '/periodic_reception', '/periodic_reception/<int:periodic_reception_id>',
                     '/periodic_reception/csv_template')

    api.add_resource(PeriodicReceptionFiltersAPI, '/periodic_reception_filters/')

    api.add_resource(PeriodicReceptionReportAPI, '/periodic_reception_report/')

    api.add_resource(RawTableAPI, '/raw_table')

    api.add_resource(ReceptionBasketFiltersAPI, '/reception_basket_filters/')

    api.add_resource(ReceptionBasketAPI, '/reception_basket/')

    api.add_resource(PaymentFailureAPI, '/payment_failure', '/payment_failure/csv_template')

    api.add_resource(InstitutionBankAccountAPI, '/institution_bank_account', '/institution_bank_account/csv_template')

    api.add_resource(MSVScrapingAPI, '/msv_scraping', '/msv_scraping/csv_template')

    api.add_resource(StudentIncomeAPI, '/student_income')

    api.add_resource(GeneralListsAPI, '/general_lists')

    api.add_resource(GeneralBankAccountAPI, '/general_bank_account',
                     '/general_bank_account/<string:general_bank_account_id>', '/general_bank_account/csv_template')

    # Endpoint of the PDF forms generation
    api.add_resource(PdfGeneratorResource, '/generate_pdf')

    # Endpoint of the Form Attributes getter
    api.add_resource(FormAttributesResource, '/form_attributes')

    # Validation of bank account
    api.add_resource(ValidationAccountAPI, '/bank_account_validation')

    # Validation of passport id by country
    api.add_resource(ValidationPassportAPI, '/passport_id_validation')

    # Validation of phone number
    api.add_resource(ValidationPhoneNumberAPI, '/phone_number_validation')

    # Generate Form
    api.add_resource(FormPDFGenerator, '/generate_form')

    # Hello world api test
    api.add_resource(HelloWorldApiTest, '/hello_world_api')

    # Validation local phone number
    api.add_resource(ValidationLocalPhoneNumber, '/local_phone_number_validation')

    # get opt
    api.add_resource(GetOpt, '/get_opt')

    api.add_resource(PaymentCheckGeneratorAPI, '/payment_check_generator')

    api.add_resource(TalmudAPI, '/talmud')
    api.add_resource(TalmudProgressAPI, '/talmud_progress')
    api.add_resource(TalmudDownloadAPI, '/talmud_download')
    api.add_resource(DownloadTemplateAPI, '/download_template')



    IndexAPI.register_error_handlers(app)
