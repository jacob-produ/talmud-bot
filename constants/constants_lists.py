EXPENSE_PAYMENT_STATUS = ["טיוטה", "הודפס", "נמסר", "נפרע", "חזר", "בוטל"]
EXPENSE_PAYMENT_METHODS = ["שיק", "מסב", "הוראת קבע", "מזומן", "העברה בנקאית"]
EXPENSE_PAYMENT_CLASSIFICATION = ["משכורת", "ספק", "תלמיד", "תלמיד לא רשום"]

INCOME_PAYMENT_METHODS = ["שיק", "מזומן", "הוראת קבע", "מסב", "אשראי", "העברה בנקאית"]
INCOME_PAYMENT_STATUS = ["טיוטה", "הכנסה צפויה", "נפרע", "חזר", "בוטל רטרו", "הודפס"]
INCOME_SOURCE = ["שכר לימוד", "תרומות", "תקצוב עירוני", "תקצוב ממשלתי", "זמני"]

EDUCATION_INCOME_PAYMENT_STATUS = ["הכנסה צפויה", "נפרע"]
ENROLLMENT_STATUS = ["פעיל", "ממתין למחיקה", "ממתין לרישום", "ממתין לקליטה", "בוטל רטרו"]
SERVICE_STATUS = ["צבאי", "אזרחי", "לאומי", "לא רלוונטי"]
DONATOR_TYPE = ["פרטי", "עוסק", "ארגון", "גוף ממשלתי"]

PERIODIC_RECEPTION_STATUS = ["פעיל", "ממתין לקבלת הרשאה", "מושהה", "הרשאה בוטלה", "הסתיים"]
PERIODIC_RECEPTION_METHODS = ['מסב', 'אשראי']
PERIODIC_RECEPTION_BANK_APPLICANT = ['בעל החשבון', 'מורשה גבייה']

SCHOLARSHIP_TYPES = ["מלגת קיום", "מלגת בסיס", "מלגת תוספת מנחה", "מלגת הוראה", "מלגת בסיס בוטלה רטרו",
                     "מלגת בסיס מקדמה"]
SCHOLARSHIP_METHODS = ["בסיס", "בסיס ותוספות", "בסיס ותוספות fixed"]

ATTRIBUTIONS = dict(עובדים="employee", ספקים='supplier', תלמידים='student')

STUDENT_IDENTITY_TYPES = ["דרכון", "תעודת זהות"]

GENERAL_BANK_ACCOUNT_STATUS = ["ברירת מחדל", "משני", "שגוי", "בן זוג", "ישן", "חיצוני"]

ATTRIBUTIONS = ["student", "employee", "supplier", "donator"]

COURSE_ENROLLMENT_REGISTRATION_STATUS = ["ממתין לשיבוץ", "ממתין לרישום", "ממתין לקליטה", "תיקון שגיאות", "ממתין למחיקה",
                                         "נמחק"]
COURSE_ENROLLMENT_REGISTRATION_TYPE = ["קליטה חדשה", "מעבר בין מוסדות", "מעבר בין סניפים", "מעבר בין מסלולים"]

EXCEL_EXTENSIONS = ['xlsx', 'xls']

ELIGIBILITY_METHODS = ["A", "B", "C", "D"]

UPLOAD_SOURCES = ["CSV", "GOOGLE-SHEETS", "API"]

TREND_COORDINATOR_STUDY_HOURS_RANGE = ["יום שלם", "בוקר", "צהריים", "בוקר וצהריים", "ערב"]
VOLUNTEER_HOURS = ["בוקר", "צהריים"]
