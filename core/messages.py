import os
import datetime

SYSTEM_LOG_FILE_FULL_PATH = "log.txt"
LOG_MAX_SIZE = 500000  # In KB (total of 500 MB)


def log_message(label, message):
    """
    Logging strategy, file, db, console, can be modified to whatever. print log and write into log file
    :param label: Label of the log record (error / warning / info)
    :param message: Message to be recorded
    :return: None
    """

    print("{} {}".format(label, message))

    reading_method = "a"

    # If file exists and exceeded maximum length, reset it.
    try:
        if os.stat(SYSTEM_LOG_FILE_FULL_PATH).st_size > LOG_MAX_SIZE:
            reading_method = "w"
    except FileNotFoundError:
        pass

    if SYSTEM_LOG_FILE_FULL_PATH:
        with open(SYSTEM_LOG_FILE_FULL_PATH, reading_method) as log_file:
            log_file.write(datetime.datetime.now().isoformat() + " {} {}".format(label, message) + "\n")


def reset_log_file():
    if SYSTEM_LOG_FILE_FULL_PATH:
        open(SYSTEM_LOG_FILE_FULL_PATH, "w").close()


LABEL_INFO = "[INFO]"
LABEL_ERROR = "[ERROR]"
LABEL_WARNING = "[WARNING]"

STR_ERROR = "error"
STR_MESSAGE = "message"

# SCHOOL MANAGER

""" crud mixin - DB messages """
READ_NO_DATA_FAIL = "There is no data for the requested filters"
READ_FAIL = "There is no {} for the requested filters"
CREATE_SUCCESS = "{} has been successfully created"
UPDATE_SUCCESS = "{} has been successfully updated"
DELETE_SUCCESS = "{} has been successfully deleted"
DELETE_FAIL = "{} has not been deleted"
CREATE_FAIL = "Could not create {}"
CREATE_NO_DATA = "There is no records to insert"
CREATE_FAIL_DUPLICATE = "Could not create {}s because of duplicates"
UPLOAD_ACTIVATION_FILE_FAIL = "Upload file failed, try again later!"
MULTIPLE_CREATE_ERRORS = "Multiple create errors. {} out of {} has been successfully created"
MULTIPLE_DELETE_ERRORS = "Multiple delete errors. {} out of {} has been successfully deleted"
ACTIVATION_SUCCESS = "Upload successfully!"
DOWNLOAD_ACTIVATION_FILE_FAIL = "Download code.dat failed, try again later!"
COLUMN_MANDATORY = "{} field is mandatory"
COLUMN_DELETE_SUCCESSFULLY = "{} has been successfully deleted."
COLUMN_DELETE_FAILED = "{} delete has failed."
NO_UPDATE_PERFORMED = r"The data {} do not exist on table {}, no update has been performed."
SERVER_ERROR = "Server error."

# TODO: transfer to school manager project
LINK_MESSAGE = "Link to record"
LINK_GENERAL_ERROR = "Could not make link to Current Account record"
LINK_WRONG_AMOUNT_MESSAGE = "The transaction amount should be {}"
LINK_NO_CASE = "The action for the description '{}' is undefined"
LINK_NO_CHECK_ERROR = "Could not find check with number {}"
LINK_CHECK_CASE_ERROR = "There is no implemented case for the check {}"
LINK_TYPE_ERROR = "Wrong Link Type."
NO_LINK_ERROR = "The Record is not linked."

CLEARING_NO_TRANSACTION_NUMBER = "Record does not contains transaction number"
CLEARING_TRANSACTION_GAP = "Missing transaction. last transaction number is {} and current transaction {}. please fill the missing transaction."
CLEARING_TRANSACTION_DUPLICATE = "Duplicate transaction. Current transaction number ({}) has already been submitted."

FIELD_FILTER_NOT_FOUND = "Could not find {} with that information"

REQUEST_EMPTY_FILE_ERROR = "Cannot read from file, the file is empty."
REQUEST_FILE_NOT_FOUND_ERROR = "Cannot find file."
REQUEST_WRONG_FORM_PARAMETERS = "Cannot read necessary form parameters."
REQUEST_WRONG_FORM_PARAMETERS_EXTENDED = "Cannot read necessary form parameters - {}."
REQUEST_CREATE_ZIP_SUCCESS = "Zip file for {} has been successfully created"


MERGE_PAYMENT_ERROR = 'Failed merging payments'
MERGE_PAYMENT_SUCCESS = 'Success merging payments'

SPLIT_PAYMENT_SUCCESS = 'Success splitting payments'
SPLIT_PAYMENT_ERROR = 'Failed splitting payments'


UPLOAD_POP_UP_SUCCESS_MESSAGE = "{}/{} רשומות התווספו בהצלחה לטבלה {}."
