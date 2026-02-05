import datetime
from school_manager.models.bank_account import BankAccount
from school_manager.models.current_account import CurrentAccount,LinkCurrentAccount,LinkCACases
from school_manager.db import db
from school_manager.constants.constants import NEW_LINE, UT8_WITH_BOM_ENCODING, WINDOWS_1255_ENCODING
from school_manager.constants import constants
import csv,os
from io import StringIO
from flask import  jsonify


def create_ca_record():
    ca = CurrentAccount()
    ca.transaction_amount = 400
    ca.transaction_description = "Student Payment"
    ca.balance = 2400
    ca.reference_number = 13971313
    ca.value_date = datetime.datetime.utcnow().isoformat()
    ca.date = datetime.datetime.utcnow().isoformat()
    ca.fk_bank_account_id = 2

    db.session.add(ca)
    db.session.commit()
    print("Done")

def create_ca_from_csv():
    pass



def create_link_to_ca(csv_path):
    CSV_ROWS_TO_SKIP = 13
    current_account_csv_file = open(csv_path, "rb")
    current_account_csv_data = current_account_csv_file.read()
    current_account_csv_file.close()
    try:
        # Try to decode the CSV data with 'windows-1255' encoding
        current_account_csv_data = current_account_csv_data.decode(WINDOWS_1255_ENCODING).split(NEW_LINE)
    except UnicodeDecodeError:
        # Try to decode the CSV data with 'UTF-8-WITH-BOM' encoding
        current_account_csv_data = current_account_csv_data.decode(UT8_WITH_BOM_ENCODING).split(NEW_LINE)

    # Skip the rows that do not contain tabular data
    current_account_csv = StringIO(NEW_LINE.join(current_account_csv_data[CSV_ROWS_TO_SKIP:]))
    try:
        bank_account_id, fk_institution_id = CurrentAccount.get_bank_account_from_csv(current_account_csv_data[:CSV_ROWS_TO_SKIP])
    except Exception as err:
        return jsonify({
            constants.STR_MESSAGE: str(err), constants.STR_ERROR: True
        })

    csv_reader = csv.DictReader(current_account_csv)
    data, fk_institution_id = CurrentAccount.create_from_csv(csv_reader, bank_account_id, fk_institution_id,os.path.basename(csv_path))
    print (data)
    for record in data:
        case_method = LinkCurrentAccount.find_link(record['transaction_description'])
        if case_method is None or case_method != LinkCACases['FEE']['METHOD']:
            continue
        current_account_record = CurrentAccount.create(record)
        if current_account_record[constants.STR_ERROR]:
            return current_account_record

        case_method(**record,fk_institution_id=fk_institution_id,fk_current_account_id=current_account_record.id)


if __name__ == '__main__':
    create_link_to_ca(r"C:\Users\Roi\Documents\Work\אבישי\csv to index\current_account.csv")