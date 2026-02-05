from school_manager.constants.constants_lists import *
from school_manager.modules.exceptions import *
from school_manager.constants.course_types import *


class ConstantsValidation:

    @staticmethod
    def expense_payment_status_validation(expense_payment_status):
        if expense_payment_status is None or expense_payment_status.strip() in EXPENSE_PAYMENT_STATUS:
            return
        raise ExpensePaymentStatusConstantNotFound(expense_payment_status)

    @staticmethod
    def expense_payment_method_validation(expense_payment_method):
        if expense_payment_method is None or \
                expense_payment_method.strip() in EXPENSE_PAYMENT_METHODS:
            return
        raise ExpensePaymentMethodConstantNotFound(expense_payment_method)

    @staticmethod
    def expense_payment_classification_validation(expense_payment_classification):
        if expense_payment_classification is None or \
                expense_payment_classification.strip() in EXPENSE_PAYMENT_CLASSIFICATION:
            return
        raise ExpensePaymentClassificationConstantNotFound(expense_payment_classification)

    @staticmethod
    def income_payment_status_validation(income_payment_status):
        if income_payment_status is None or \
                income_payment_status.strip() in INCOME_PAYMENT_STATUS:
            return
        raise IncomePaymentStatusConstantNotFound(income_payment_status)

    @staticmethod
    def income_payment_method_validation(income_payment_method):
        if income_payment_method is None or \
                income_payment_method.strip() in INCOME_PAYMENT_METHODS:
            return
        raise IncomePaymentMethodConstantNotFound(income_payment_method)

    @staticmethod
    def income_source_validation(income_source):
        if income_source is None or \
                income_source.strip() in INCOME_SOURCE:
            return
        raise IncomeSourceConstantNotFound(income_source)

    @staticmethod
    def education_income_payment_validation(education_income_payment):
        if education_income_payment is None or \
                education_income_payment.strip() in EDUCATION_INCOME_PAYMENT_STATUS:
            return
        raise EducationIncomePaymentConstantNotFound(education_income_payment)

    @staticmethod
    def enrollment_status_validation(enrollment_status):
        if enrollment_status is None or \
                enrollment_status.strip() in ENROLLMENT_STATUS:
            return
        raise EnrollmentStatusConstantNotFound(enrollment_status)

    @staticmethod
    def service_status_validation(service_status):
        if service_status is None or \
                service_status.strip() in SERVICE_STATUS:
            return
        raise ServiceStatusConstantNotFound(service_status)

    @staticmethod
    def donator_type_validation(donator_type):
        if donator_type is None or \
                donator_type.strip() in DONATOR_TYPE:
            return
        raise DonatorTypeConstantNotFound(donator_type)

    @staticmethod
    def periodic_reception_status_validation(periodic_reception_status):
        if periodic_reception_status is None or \
                periodic_reception_status.strip() in PERIODIC_RECEPTION_STATUS:
            return
        raise PeriodicReceptionStatusConstantNotFound(periodic_reception_status)

    @staticmethod
    def periodic_reception_method_validation(periodic_reception_method):
        if periodic_reception_method is None or \
                periodic_reception_method.strip() in PERIODIC_RECEPTION_METHODS:
            return
        raise PeriodicReceptionMethodConstantNotFound(periodic_reception_method)

    @staticmethod
    def periodic_reception_bank_applicant_validation(periodic_reception_bank_applicant):
        if periodic_reception_bank_applicant is None or \
                periodic_reception_bank_applicant.strip() in PERIODIC_RECEPTION_BANK_APPLICANT:
            return
        raise PeriodicReceptionBankApplicantConstantNotFound(periodic_reception_bank_applicant)

    @staticmethod
    def scholarship_type_validation(scholarship_type):
        if scholarship_type is None or \
                scholarship_type.strip() in SCHOLARSHIP_TYPES:
            return
        raise ScholarshipTypeConstantNotFound(scholarship_type)

    @staticmethod
    def scholarship_method_validation(scholarship_method):
        if scholarship_method is None or \
                scholarship_method.strip() in SCHOLARSHIP_METHODS:
            return
        raise ScholarshipMethodConstantNotFound(scholarship_method)

    @staticmethod
    def study_hours_range_validation(study_hours_range):
        if study_hours_range is None or \
                study_hours_range.strip() in TREND_COORDINATOR_STUDY_HOURS_RANGE:
            return
        raise ScholarshipMethodConstantNotFound(study_hours_range)

    @staticmethod
    def student_identity_type_validation(student_identity_type):
        if student_identity_type is None or student_identity_type.strip() in STUDENT_IDENTITY_TYPES:
            return
        raise StudentIdentityTypeConstantNotFound(student_identity_type)

    @staticmethod
    def general_bank_account_status_validation(general_bank_account_status):
        if general_bank_account_status is None or \
                general_bank_account_status.strip() in GENERAL_BANK_ACCOUNT_STATUS:
            return
        raise GeneralBankAccountConstantNotFound(general_bank_account_status)

    @staticmethod
    def course_enrollment_registration_status_validation(course_enrollment_registration_status):
        if course_enrollment_registration_status is None or \
                course_enrollment_registration_status.strip() in COURSE_ENROLLMENT_REGISTRATION_STATUS:
            return
        raise CourseEnrollmentRegistrationStatusConstantNotFound(course_enrollment_registration_status)

    @staticmethod
    def course_enrollment_registration_type_validation(course_enrollment_registration_type):
        if course_enrollment_registration_type is None or \
                course_enrollment_registration_type.strip() in COURSE_ENROLLMENT_REGISTRATION_TYPE:
            return
        raise CourseEnrollmentRegistrationTypeConstantNotFound(course_enrollment_registration_type)

    @staticmethod
    def eligibility_method_validation(eligibility_method):
        if eligibility_method is None or \
                eligibility_method.strip().upper() in ELIGIBILITY_METHODS:
            return
        raise EligibilityMethodConstantNotFound(eligibility_method)

    @staticmethod
    def course_type_validation(course_type):
        if course_type is None or \
                course_type.strip() in [str(course) for course in COURSE_TYPE_MAP.keys()]:
            return
        raise CourseTypeConstantNotFound(course_type)

    @staticmethod
    def day_part_validation(day_part):
        if day_part is None or \
                day_part.strip() in list(COURSE_TYPE_DAY_PART_MAP_REVERSED.keys()):
            return
        raise DayPartConstantNotFound(day_part)
