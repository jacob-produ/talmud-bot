import os

EMPTY_STRING = ""
STR_DATA = "data"
STR_TYPE = "type"
STR_ERROR = "error"
STR_VALUE = "value"
STR_MESSAGE = "message"
STR_FILE_DATA = "file_data"
STR_ERROR_CODE = "error_code"
STR_TASK_ID = "task_id"
STR_SETTING_ID = "setting_id"
STR_DUPLICATE = "duplicate"
WEB_SERVER_LISTENING_IP = "0.0.0.0"
ROLE_ADMIN = "admin"

UT8_WITH_BOM_ENCODING = 'utf-8-sig'
UT16_WITH_BOM_ENCODING = 'utf-16-le'
WINDOWS_1255_ENCODING = 'windows-1255'

NEW_LINE = "\n"

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

SERVER_UI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "user_interface"))

IP_ADDRESSES = {
    "PROD": "50.21.190.74",
    "DEV": "198.251.77.240",
    # "test": "77.68.120.107"
}

DEFAULT_IP_ADDRESS = IP_ADDRESSES["PROD"]
# DEFAULT_IP_ADDRESS = IP_ADDRESSES["DEV"]
DEFAULT_CONFIG_FILE_PATH = "/home/config.ini"
