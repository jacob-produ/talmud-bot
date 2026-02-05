
'''
The following dictionary defines for each form (which identified by its name)
its properties and their type.

Note:
    1. Type names were defined according to the HTML attribute values. The type names are likely to get updates
        during integration.
    2. TODO (optionally): In order to be able to update this dictionary in the future
        we'll need to load this file during start-up (with a loader class)

'''

FORM_PROPERTIES = {
    'property-tax-form': {
        'student_full_name': {'type': 'text', 'display_name':'שם התלמיד' },
        'student_identity': {'type': 'number', 'display_name': 'ת.ז תלמיד'},
        'generated_form_payment_amount': {'type': 'number', 'display_name': 'סך מלגה'},
        'generated_form_approval_period': {'type': 'radio', 'values': [1,2,3,4], 'display_name':'לתקופה'},
        'generated_form_previous_payments': {'type': 'text', 'display_name':'תשלומים קודמים'},
        'committee_member_full_name': {'type': 'text', 'display_name':'שם מלא חבר ועד'},
        'committee_member_identity': {'type': 'number', 'display_name': 'ת.ז חבר ועד'},
        'committee_member_role': {'type': 'text', 'display_name':'תפקיד' },
    },

    'social-services-form': {
        'institution_short_name': {'type': 'text', 'display_name':'שם מוסד' },
        'institution_full_address': {'type': 'text', 'display_name':'כתובת המוסד' },
        'institution_identity': {'type': 'number', 'display_name': 'מזהה מוסד'},
        'institution_phone_number': {'type': 'number', 'display_name': 'מספר טלפון מוסד'},
        'student_full_name': {'type': 'text', 'display_name': 'שם התלמיד'},
        'student_identity': {'type': 'number', 'display_name': 'ת.ז תלמיד'},
        'course_start_date': {'type': 'date', 'display_name': 'תאריך תחילת הקוס'},
        'committee_member_full_name': {'type': 'text', 'display_name': 'שם מלא חבר ועד'},
        'committee_member_type': {'type': 'radio', 'values': ['ת.ז','דרכון'], 'display_name': 'סוג מזהה חבר ועד'},
        'form_generation_date': {'type': 'date', 'display_name': 'תאריך יצירת הדוח'},
        'committee_member_signature': {'type': 'text', 'display_name': 'חתימת חבר ועד (URL)'},
        'committee_member_stamp': {'type': 'text', 'display_name': 'חותמת חבר ועד (URL)'},
    },

    'student-approval-form': {
        'student_full_name': {'type': 'text', 'display_name': 'שם התלמיד'},
        'student_identity': {'type': 'number', 'display_name': 'ת.ז תלמיד'},
        'committee_member_full_name': {'type': 'text', 'display_name': 'שם מלא חבר ועד'},
        'committee_member_identity': {'type': 'text', 'display_name': 'ת.ז חבר ועד'},
        'committee_member_role': {'type': 'text', 'display_name': 'תפקיד חבר ועד'},
    },

    'student-approval-form-with-course': {
        'student_first_name': {'type': 'text', 'display_name': 'שם פרטי'},
        'student_last_name': {'type': 'text', 'display_name': 'שם משפחה'},
        'student_identity_type': {'type': 'radio', 'values': ['ת.ז', 'דרכון'], 'display_name': 'סוג מזהה'},
        'student_identity': {'type': 'number', 'display_name': 'מספר זיהוי'},
        'student_birth_date': {'type': 'date', 'display_name': 'תאריך לידה'},
        'student_marital_status': {'type': 'text', 'display_name': 'סטטוס'},
        'student_birth_state': {'type': 'text', 'display_name': 'ארץ לידה'},
        'student_support_period': {'type': 'number', 'display_name': 'תקופת תמיכה (בחודשים)'},
        'institution_name': {'type': 'text', 'display_name': 'שם המוסד'},
        'static_mapping_course_type': {'type': 'text', 'display_name': 'סוג מסלול'},
        'course_enrollment_course_type': {'type': 'text', 'display_name': 'שם סוג מסלול'},
        'static_mapping_course_name': {'type': 'text', 'display_name': 'שם המסלול'},
    },
}
