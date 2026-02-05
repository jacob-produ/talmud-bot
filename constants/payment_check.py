import os
from pathlib import Path

# INPUT_FILE_FIELDS
BANK_ACCOUNT_NUMBER = "account_number"
PREVIOUS_BANK_ACCOUNT = "prev_account_number"
INSTITUTION_NAME = "institution_name"
ASSOCIATION_NUMBER = "association_num"  ##
BANK_BRANCH_MAIL_NUMBER = "mail_num"  ##
BANK_PHONE = "bank_phone_number"
BANK_NUM = "bank_number"
BANK_BRANCH_NAME = "branch_name"
BANK_BRANCH_NUMBER = "branch_number"
BANK_MAIL_ADDRESS = "bank_mail_num_and_address"  ##
INSTITUTION_PHONE_NUMBER = "institution_phone_number"
CHECK_NUMBER = "check_number"
CREATE_DATE = "date"  ##
CREATE_MONTH = "for_month"  ##
RECIPIENT_NAME = "full_name"
AMOUNT = "amount"

# Generated Fields
AMOUNT_IN_WORDS = "amount_in_words"
BRANCH_AND_NUM = "branch_and_num"
BANK_PHONE_AND_ADDRESS = "bank_phone_and_address"

SIGNATURE = "signature"

# Constants
CHECKS_PER_PAGE = 4

HEB_LANG = "hebrew"

# Paths
HOME_PATH = Path(__file__).resolve().parent.parent
CHECK_TEMPLATE_FILE_PATH = os.path.join(HOME_PATH, "assets/payment_check/files/mercantil.pdf")
OUTPUT_PAYMENT_FILE_PATH = os.path.join(HOME_PATH, "~/Documents/signature.jpg")
if not os.path.exists(OUTPUT_PAYMENT_FILE_PATH):
    SIGNATURE_FILE_PATH = os.path.join(HOME_PATH, "assets/payment_check/files/signature.jpg")
OUTPUT_PAYMENT_FILE_PATH = os.path.join(HOME_PATH, "assets/payment_check/files/generated_checks.pdf")
AARONI_FONT_PATH = os.path.join(HOME_PATH, "assets/payment_check/fonts/Aharoni.ttf")
ARIAL_FONT_PATH = os.path.join(HOME_PATH, "assets/payment_check/fonts/Arial.ttf")
IDAUTOMATION_FONT_PATH = os.path.join(HOME_PATH, "assets/payment_check/fonts/IDAutomation.ttf")
PAYMENT_CHECKS_TEMPLATE_FILE_PATH = os.path.join(HOME_PATH,'assets/payment_check/files/payment_checks_template.xlsx')

AARONI_FONT = "Aaroni"
ARIAL_FONT = "Arial"
IDAUTOMATION_FONT = "IDAutomation"
ACCOUNT_DETAILS = "account_details"
BARCODE = "barcode"

# The spaces between checks.
MARGIN = [0, 209, 418, 627]

START_COORDINATES = "coordinates"
FONT = "font"
RTL = "right_to_left"

# The coordinates data for each field.
INPUT_POS_DATA = {
    BANK_ACCOUNT_NUMBER: [{START_COORDINATES: (417, 860), FONT: (AARONI_FONT, 10), RTL: False}],
    PREVIOUS_BANK_ACCOUNT: [{START_COORDINATES: (350, 860), FONT: (AARONI_FONT, 10), RTL: False}],
    INSTITUTION_NAME: [{START_COORDINATES: (470, 850), FONT: (AARONI_FONT, 10), RTL: True}],
    ASSOCIATION_NUMBER: [{START_COORDINATES: (417, 838.5), FONT: (AARONI_FONT, 10), RTL: False}],
    BANK_BRANCH_MAIL_NUMBER: [{START_COORDINATES: (417, 828.5), FONT: (AARONI_FONT, 10), RTL: False}],
    INSTITUTION_PHONE_NUMBER: [{START_COORDINATES: (307, 829), FONT: (AARONI_FONT, 10), RTL: False}],
    BRANCH_AND_NUM: [{START_COORDINATES: (30, 821), FONT: (AARONI_FONT, 11), RTL: False}], ##
    CREATE_MONTH: [{START_COORDINATES: (530, 843), FONT: (AARONI_FONT, 10), RTL: False}],
    RECIPIENT_NAME: [{START_COORDINATES: (540, 830), FONT: (AARONI_FONT, 11), RTL: True},
                     {START_COORDINATES: (260, 788), FONT: (AARONI_FONT, 11), RTL: True}],
    AMOUNT: [{START_COORDINATES: (520, 802), FONT: (AARONI_FONT, 10), RTL: False},
             {START_COORDINATES: (417, 769), FONT: (AARONI_FONT, 14), RTL: False}],
    CREATE_DATE: [{START_COORDINATES: (510, 787), FONT: (AARONI_FONT, 10), RTL: False},
                  {START_COORDINATES: (220, 730), FONT: (AARONI_FONT, 12), RTL: False}],
    CHECK_NUMBER: [{START_COORDINATES: (510, 769), FONT: (AARONI_FONT, 10), RTL: False}],
    AMOUNT_IN_WORDS: [{START_COORDINATES: (300, 765), FONT: (AARONI_FONT, 10), RTL: True}],
    BANK_PHONE_AND_ADDRESS: [{START_COORDINATES: (30, 810), FONT: (AARONI_FONT, 11), RTL: False}],
    ACCOUNT_DETAILS: [{START_COORDINATES: (30, 800), FONT: (AARONI_FONT, 11), RTL: False}],
    BARCODE: [{START_COORDINATES: (30, 695), FONT: (IDAUTOMATION_FONT, 14), RTL: False}],
    SIGNATURE: [{START_COORDINATES: (390, 725), FONT: (AARONI_FONT, 12), RTL: False}]
}