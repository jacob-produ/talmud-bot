import os
THREADS_COUNT = 4
PROXY_ENABLED = True
PROXY_SERVER = "socks5://127.0.0.1:1080"
PROXIES = {"http": PROXY_SERVER, "https": PROXY_SERVER}

CHROME_ARGUMENTS = ["--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage"]

if not os.name == "nt":
    CHROME_ARGUMENTS.append("--headless")
    CHROME_ARGUMENTS.append("--headless=new")

CHROME_EXPERIMENTAL = [("excludeSwitches", ["enable-automation"]),
                       ("useAutomationExtension", False),
                       ("detach", True)]

PREFS = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
}


DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(DIR_PATH,'assets/talmud/config.ini')
PAYMENTS_CHECK_TEMPLATE_FILE_PATH = os.path.join(DIR_PATH,'assets/talmud/files/payment_checks_template.xlsx')
TALMUD_TEMPLATE_FILE_PATH = os.path.join(DIR_PATH,'assets/talmud/files/talmud_template.xlsx')
ADD_STUDENTS_TEMPLATE_FILE_PATH = os.path.join(DIR_PATH,'assets/talmud/files/add_students_template.xlsx')
UPLOAD_ADD_FILE_PATH = os.path.join(DIR_PATH,'assets/talmud/files/temp_upload_add.xlsx')

LOG_FILE_PATH = "log.txt"
if os.name == 'posix':
    LOG_FILE_PATH = os.path.join(DIR_PATH, "log.txt")

RESULTS_FOLDER_NAME = os.path.join(DIR_PATH,"results")
RESULTS_FILE_NAME = "result_{}.xlsx"
RESULTS_FAILURES_FILE_NAME = "failures_{}.xlsx"

# Tasks types
TASK_ADD_STUDENTS = "add_students"
TASK_REMOVE_STUDENTS = "remove_students"
TASK_APPROVE_STUDENTS = "approve_students"
TASK_REJECT_STUDENTS = "reject_students"

PRINT_PROCESS_THRESHOLD = 10

# Base headers used for all requests
HEADERS = {
    "Host": "talmud.edu.gov.il",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Microsoftajax": "Delta=true"
}
REMOVE_STUDENT_SERVER_SUCCESS_MESSAGE = "תהליך עידכון תלמיד הצליח"

DEPARTURE_REASON_CODE = 3

MAX_SAVE_ATTEMPTS = 5

# Results file fields.
STUDENT_ID_COL_NAME = "StudentIdentity"
STUDY_TYPE_COL_NAME = "StudyTypeID"
BRANCH_COL_NAME = "Textbox237"
DEPARTED_COL_NAME = "departed"
DETAILS_COL_NAME = "DETAILS"
ACTION_COL_NAME = "action_to_perform"

ACTION_DECLINE_CODE = 0
ACTION_APPROVE_CODE = 1

RESULTS_SUCCESS = "success"
RESULTS_FAILURE = "failure"
RESULTS_SUCCESS_MESSAGE = "Departed successfully"
RESULTS_REASON_STUDENT_NOT_FOUND = "Student not found"
RESULTS_REASON_SELECT_STUDENT_FAILED = "Student select failed"
RESULTS_REASON_DEPARTURE_STUDENT_FAILED = "Student departure failed"
RESULTS_REASON_SAVE_FAILED = "Student save failed"

# Students transfer
TRANSFER_APPROVED = "approved"
TRANSFER_DENIED = "denied"

# Log labels
LABEL_ERROR = "[ERROR]"
LABEL_WARNING = "[WARNING]"
LABEL_INFO = "[INFO]"

# Log messages
DEPARTURE_START = "Talmud - students departure process started."
DEPARTURE_END = "Talmud - students departure process ended."
PROGRESS_DEPARTED = "{} / {} students have been departure so far."
PROGRESS_PROCESSED = "{} / {} students have been processed so far."
STUDENT_NOT_FOUND = "Failed to find student id: {} with study type: {}. The student may not be active."
FAILED_TO_SAVE_CHANGES = "Failed to save changed on the server."
UNSUPPORTED_INPUT_FILE = "Unsupported file format. Only CSV and XLSX are supported."
ERROR_IN_THREAD = "Error in thread execution: {}"
CREDENTIALS_ERROR = "Error with cookies or viewstate_key.. please check your login credentials"
DEPARTURE_BY_BRANCH_START = "Starting departure all students from branch {}"
REQUEST_RESPONSE_NOT_OK = "The request {} return code {}"
CREATING_NEW_SESSION = "Creating new selenium session"
SELENIUM_LOGIN_SUCCESS = "Login successful using Selenium"
SELENIUM_LOGIN_FAIL = "Login failed using Selenium"
SELENIUM_VIEWKEY_FAIL = "Failed to retrieve __VIEWSTATE_KEY"
RESULTS_FILE_CREATED = "Results file created"
RESULTS_FAILURES_FILE_CREATED = "Failures file created"
RUN_END_WITH_FAILURE = "\nThe last run ended with error. \nWould you like to perform re-run on students who did not departed? \nY/N?"
INVALID_INPUT = "Invalid input, please answer with 'Y' or 'N'"
GOODBYE = "Have a nice day, goodbye :)"

TRANSFER_START = "Talmud - approve transfer process started."
TRANSFER_END = "Talmud - approve transfer process ended."
TRANSFER_PERFORMED = "For student {} the transfer request has been {}"
NO_ACTION_PERFORMED = "No action performed for the following students: {}"
ADD_START = "Talmud - add students process started."
ADD_END = "Talmud - add students process ended."
NO_ACTION_FOUND = "פעולה לא תקינה."
TRANSFER_SUCCESS = "פעולה בוצעה בהצלחה."
ADD_STUDENT_SUCCESS = "תלמיד נוסף בהצלחה."
ADD_SUCCESS = ("\nפעולה הסתיימה בהצלחה."
               "תוצאות הריצה {}/{} נוספו בהצלחה.\n"
               "ראה קובץ סיכום ריצה לפירוט.\n")
CREDENTIALS_MISSING = "credentials_missing"
NO_FILE_SELECTED = "קובץ קלט לא הועלה."
NO_DATA_TO_PROCESS = "קובץ לא מכיל מידע לעיבוד"
FILE_TYPE_NOT_SUPPORTED = "קובץ הקלט בפורמט לא תקין. אנא העלה קובץ xlsx"
ADD_BRANCH_NOT_FOUND = "סניף {} לא נמצא"
ADD_STUDY_NOT_FOUND = "סוג הלימוד {} לא נמצא עבור סניף {}"
STUDENT_TRANSFER_NEEDED = "סטודנט {} כבר רשום בסניף {} לסוג לימוד אחר, פעולה בוטלה"
STUDENT_ALREADY_REGISTERED = "סטודנט {} כבר רשום בסניף {} לסוג לימוד {}"
STUDENT_TRANSFER_SUCCESS = "סטודנט הועבר בהצלחה"
STUDENT_ADDED_SUCCESS = "סטודנט נוסף בהצלחה"

SUMMARY = "\n-------------CONCLUSION------------- \n{} / {} students have been departure \n{} / {} students have been processed. \n------------------------------------"
S_SUMMARY = "\n {} / {} students have been departure \n{} / {} students have been processed. \n"
