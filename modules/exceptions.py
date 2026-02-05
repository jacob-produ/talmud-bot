class NoneValueException(Exception):
    def __init__(self, parameter_name=""):
        super().__init__(f"The value of {parameter_name} is null")


class StudentNotExist(Exception):
    def __init__(self, identity):
        self.message = f"There is no student with identity {identity}"
        super().__init__(self.message)

class EmployeeNotExist(Exception):
    def __init__(self, identity):
        self.message = f"There is no employee with identity {identity}"
        super().__init__(self.message)

class SupplierNotExist(Exception):
    def __init__(self, identity):
        self.message = f"There is no supplier with identity {identity}"
        super().__init__(self.message)

class CourseEnrollmentNotExist(Exception):
    def __init__(self):
        super().__init__(f"There is no course enrollment to the student with that course type in this branch")


class InstitutionNotExist(Exception):
    def __init__(self, identity):
        self.message = f"There is no institution with identity {identity}"
        super().__init__(self.message)

class BranchNotExist(Exception):
    def __init__(self, institution_identity, symbol):
        super().__init__(f"There is no branch with symbol {symbol} of institution {institution_identity}")

class CourseEnrollmentAttributionError(Exception):
    def __init__(self, trend_coordinator_id):
        super().__init__(f"There is no course enrollment to attribute for trend coordinator attribution with id {trend_coordinator_id}")

class ExcellenceAllotmentError(Exception):
    def __init__(self,suffix):
        super().__init__(f"Could Not make allotment for the record - {suffix}")


class UpdateIncomeError(Exception):
    def __init__(self, message=''):
        super().__init__(f"Could Not update old income")
        self.message = message

class IncomeNotFoundError(Exception):
    def __init__(self, suffix):
        super().__init__(f"Could not find income with that parameters ({suffix})")

class PaymentFailureNotFoundError(Exception):
    def __init__(self, code):
        super().__init__(f"Could not find payment failure with code {code}")

class UpdateExpenseError(Exception):
    def __init__(self, message=''):
        super().__init__(f"Could Not update old income")
        self.message = message

class DeleteExpenseError(Exception):
    def __init__(self, message=''):
        super().__init__(f"Could Not update old income")
        self.message = message

class CreateInstitutionError(Exception):
    def __init__(self, identity, message=''):
        self.message = message
        super().__init__(f"Could Not create institution {identity}")

class CreateBankAccountError(Exception):
    def __init__(self, number, message=''):
        self.message = message
        super().__init__(f"Could Not create bank account {number}")

class CreateBranchError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(f"Could Not create branch.")


class CreateMSVScrapingError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(f"Could Not create msv scraping.")

class MSVScrapingNotExistError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(f"Could Not find msv scraping id.")

class CreateMSVScrapingInnerError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(f"Could Not create msv scraping inner.")

class MSVScrapingInnerTransactorNotFoundError(Exception):
    def __init__(self, identity=''):
        self.message = f'Could not find transactor with identity {identity}.'
        super().__init__(self.message)

class CreateTrendCoordinatorError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create trend coordinator.")

class UpdateTrendCoordinatorError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not update trend coordinator.")

class CreateTrendCoordinatorAttributionError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create trend coordinator attribution.")

class AttributionNotFoundError(Exception):
    def __init__(self,attribution, identity):
        self.message = f"Could Not find attribution={attribution} with id={identity}"
        super().__init__(self.message)

class TrendCoordinatorNotFoundError(Exception):
    def __init__(self, name):
        self.message =f"Could Not find trend coordinator={name}"
        super().__init__(self.message)

class TrendCoordinatorAttributionNotFoundError(Exception):
    def __init__(self):
        self.message = f"Could Not find trend coordinator attribution of the course"
        super().__init__(self.message)

class CreateCourseEnrollmentError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create trend coordinator attribution.")

class CreateMSVFileError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create msv file.")

class CreateStudentError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create student.")

class CreateSupplierError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create supplier.")

class CreateDonatorError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create donator.")

class CreateEmployeeError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create employee.")

class CreateGeneralBankAccountError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create general bank account.")

class CreatePeriodicReceptionError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create periodic reception.")

class CreateClearingPlatformError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create clearing platform.")

class CreateCurrentAccountError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create current account.")

class CreateIncomeError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create income.")

class CreatePaymentFailureError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create payment failure.")

class CreateClearingError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create clearing.")

class UpdateClearingError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create clearing.")

class ClearingTransactionNotFoundError(Exception):
    def __init__(self, suffix):
        super().__init__(f"Could Not find clearing transaction with parameters ({suffix}).")

class CreateExpenseError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create expense.")

class CreateInvoiceError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create invoice.")

class CreateStudentInsuranceError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not create student insurance.")

class LinkCurrentAccountError(Exception):
    def __init__(self,message=''):
        self.message = message
        super().__init__(f"Could Not link current account.")

class ConstantNotFound(Exception):
    def __init__(self,message):
        super().__init__(message)

class ExpensePaymentStatusConstantNotFound(ConstantNotFound):
    def __init__(self,expense_payment_status):
        super().__init__(f"There is no expense payment status such {expense_payment_status}")


class ExpensePaymentMethodConstantNotFound(ConstantNotFound):
    def __init__(self,expense_payment_method):
        super().__init__(f"There is no expense payment method such {expense_payment_method}")


class ExpensePaymentClassificationConstantNotFound(ConstantNotFound):
    def __init__(self,expense_payment_classification):
        super().__init__(f"There is no expense payment classification such {expense_payment_classification}")


class IncomePaymentStatusConstantNotFound(ConstantNotFound):
    def __init__(self,income_payment_status):
        super().__init__(f"There is no income payment status such {income_payment_status}")


class IncomePaymentMethodConstantNotFound(ConstantNotFound):
    def __init__(self,income_payment_method):
        super().__init__(f"There is no income payment method such {income_payment_method}")


class IncomeSourceConstantNotFound(ConstantNotFound):
    def __init__(self,income_source):
        super().__init__(f"There is no income source such {income_source}")

class EducationIncomePaymentConstantNotFound(ConstantNotFound):
    def __init__(self,education_income_payment):
        super().__init__(f"There is no education income payment such {education_income_payment}")

class EnrollmentStatusConstantNotFound(ConstantNotFound):
    def __init__(self,enrollment_status):
        super().__init__(f"There is no enrollment status such {enrollment_status}")

class ServiceStatusConstantNotFound(ConstantNotFound):
    def __init__(self,service_status):
        super().__init__(f"There is no service status such {service_status}")

class DonatorTypeConstantNotFound(ConstantNotFound):
    def __init__(self,donator_type):
        super().__init__(f"There is no donator type such {donator_type}")


class PeriodicReceptionStatusConstantNotFound(ConstantNotFound):
    def __init__(self,periodic_reception_status):
        super().__init__(f"There is no periodic reception status such {periodic_reception_status}")


class PeriodicReceptionMethodConstantNotFound(ConstantNotFound):
    def __init__(self,periodic_reception_method):
        super().__init__(f"There is no periodic reception method such {periodic_reception_method}")


class PeriodicReceptionBankApplicantConstantNotFound(ConstantNotFound):
    def __init__(self,periodic_reception_bank_applicant):
        super().__init__(f"There is no periodic reception bank applicant such {periodic_reception_bank_applicant}")


class ScholarshipTypeConstantNotFound(ConstantNotFound):
    def __init__(self,scholarship_type):
        super().__init__(f"There is no scholarship type such {scholarship_type}")

class ScholarshipMethodConstantNotFound(ConstantNotFound):
    def __init__(self,scholarship_method):
        super().__init__(f"There is no scholarship type such {scholarship_method}")

class StudyHoursRangeConstantNotFound(ConstantNotFound):
    def __init__(self,study_hours_range):
        super().__init__(f"There is no scholarship type such {study_hours_range}")

class StudentIdentityTypeConstantNotFound(ConstantNotFound):
    def __init__(self, student_identity_type):
        super().__init__(f"There is no student identity type such {student_identity_type}")


class GeneralBankAccountConstantNotFound(ConstantNotFound):
    def __init__(self, general_bank_account_status):
        super().__init__(f"There is no general bank account status such {general_bank_account_status}")


class CourseEnrollmentRegistrationStatusConstantNotFound(ConstantNotFound):
    def __init__(self, course_enrollment_registration_status):
        super().__init__(f"There is no course enrollment registration status such {course_enrollment_registration_status}")

class CourseEnrollmentRegistrationTypeConstantNotFound(ConstantNotFound):
    def __init__(self, course_enrollment_registration_type):
        super().__init__(f"There is no course enrollment registration type such {course_enrollment_registration_type}")

class EligibilityMethodConstantNotFound(ConstantNotFound):
    def __init__(self, eligibility_method):
        super().__init__(f"There is no eligibility method such {eligibility_method}")


class CourseTypeConstantNotFound(ConstantNotFound):
    def __init__(self, course_type):
        super().__init__(f"There is no course type such {course_type}")

class DayPartConstantNotFound(ConstantNotFound):
    def __init__(self, day_part):
        super().__init__(f"There is no day part such {day_part}")

class UploadMandatoryColumnNotFound(Exception):
    def __init__(self, mandatory_columns):
        self.message = f"All the fields: {','.join(mandatory_columns)} has to contain data."
        super().__init__(self.message)

class ClearingTransactionGapError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ClearingTransactionDuplicateError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AttributionNotExist(Exception):
    def __init__(self, attribution):
        self.message = f'There is no attribution such as {attribution}'
        super().__init__(self.message)