import datetime
from typing import List
from os import path
RECORD_LEN = 128
NEWLINE = "\r\n"
# Encoding to support hebrew
ENCODING = "cp862"


def get_reversed_heb(heb_str):
    return heb_str[::-1]


class MSVHeader:
    start_magic = 'K'
    coin = f"{0:02d}"
    serial_number = "001"
    end_magic = "KOT"

    def __init__(self, institute_code: int, sending_institute_code: int, institute_name: str):
        self.institute_code = f"{institute_code:08d}"
        self.payment_date = self.get_now_date()
        self.created_date = self.get_now_date()
        self.sending_institute_code = f"{sending_institute_code:05d}"

        if not institute_name.isascii():
            institute_name = get_reversed_heb(institute_name)

        self.institute_name = f"{institute_name[:30]:>30}"

    def get_header(self):
        header = f"{self.start_magic}{self.institute_code}{self.coin}{self.payment_date}0{self.serial_number}0" \
                 f"{self.created_date}{self.sending_institute_code}{'0'*6}{self.institute_name}{' ' * 56}" \
                 f"{self.end_magic}{NEWLINE}"

        return header.encode(ENCODING)

    @staticmethod
    def get_now_date():
        # Example - 200623 - YYMMDD
        return datetime.datetime.now().strftime('%y%m%d')


class MSVTransaction:
    # TODO:  CHECK IF ITS AUTO INCREMENT NUMBER
    start_magic = '1'
    payment_period = '0' * 8  # LEN 8 YYMMYYMM , nullable , like payment for month 06.2020
    transaction_type = '006'  # LEN 3
    bank_account_type = '0000'  # LEN 4

    def __init__(self, header: MSVHeader, bank_code: int, bank_branch_code: int, bank_account_number: int,
                 payee_tz: int, payee_name: str, payment_amount: float, payee_institution_identifier: str):
        self.header = header
        self.bank_code = f"{bank_code:02d}"
        self.bank_branch_code = f"{bank_branch_code:03d}"
        self.bank_account_number = f"{bank_account_number:09d}"
        self.payee_tz = f"{payee_tz:09d}"

        if not payee_name.isascii():
            payee_name = get_reversed_heb(payee_name)
        self.payee_name = f"{payee_name[:16]:>16}"

        self.payment_amount_float = float(payment_amount)
        self.payment_amount, self.payment_amount_remainder = str(self.payment_amount_float).split('.')
        if len(str(self.payment_amount_remainder)) == 1:
            self.payment_amount_remainder = str(int(self.payment_amount_remainder) * 10)
        self.payment_amount = f"{int(self.payment_amount[:11]):011d}"
        self.payment_amount_remainder = f"{int(self.payment_amount_remainder[:2]):02d}"

        self.payee_institution_identifier = f"{payee_institution_identifier[:20]:>20}"

    def get_transaction(self):
        transaction = f"{self.start_magic}{self.header.institute_code}{self.header.coin}{'0'*6}{self.bank_code}{self.bank_branch_code}" \
                 f"{self.bank_account_type}{self.bank_account_number}0{self.payee_tz}{self.payee_name}" \
                 f"{self.payment_amount}{self.payment_amount_remainder}{self.payee_institution_identifier}" \
                      f"{self.payment_period}{'0'*3}{self.transaction_type}{'0'*18}{' '*2}{NEWLINE}"

        return transaction.encode(ENCODING)


class MSVSumEntry:
    start_magic = '5'

    def __init__(self, header: MSVHeader, transactions: List[MSVTransaction]):
        self.header = header
        self.transactions_list = transactions

        self.transaction_sum, self.transaction_sum_remainder = str(float(self.get_transactions_sum())).split('.')
        if len(str(self.transaction_sum_remainder)) == 1:
            self.transaction_sum_remainder = str(int(self.transaction_sum_remainder) * 10)
        self.transaction_sum = f"{int(self.transaction_sum[:13]):013d}"
        self.transaction_sum_remainder = f"{int(self.transaction_sum_remainder[:2]):02d}"

        self.transaction_count = f"{len(transactions):07d}"

    def get_transactions_sum(self):
        transactions_sum = 0.0
        for transaction in self.transactions_list:
            transactions_sum += transaction.payment_amount_float

        return transactions_sum

    def get_sum_entry(self):
        sum_entry = f"{self.start_magic}{self.header.institute_code}{self.header.coin}{self.header.payment_date}0" \
                    f"{self.header.serial_number}{self.transaction_sum}{self.transaction_sum_remainder}" \
                    f"{'0'*15}{self.transaction_count}{'0'*7}{' ' * 63}{NEWLINE}"

        return sum_entry.encode(ENCODING)


class MSVFooter:
    footer_magic = f"{'9'* 128}"

    def get_footer(self):
        footer = f"{self.footer_magic}{NEWLINE}"
        return footer.encode(ENCODING)


class MSVFile:
    def __init__(self, header: MSVHeader, transactions: List[MSVTransaction], msv_path="", name="msv_file"):
        self.msv_name = f'{name}.msv'
        self.msv_path = path.join(msv_path, self.msv_name)
        self.header = header
        self.transactions_list = transactions
        self.sum_entry = MSVSumEntry(self.header, self.transactions_list)
        self.footer = MSVFooter()

    def dump(self):
        with open(self.msv_path, 'wb') as f:
            f.write(self.header.get_header())
            for transaction in self.transactions_list:
                f.write(transaction.get_transaction())
            f.write(self.sum_entry.get_sum_entry())
            f.write(self.footer.get_footer())


if __name__ == "__main__":

    mh = MSVHeader(institute_code=48296289, sending_institute_code=48296, institute_name="בית צבי העברות")

    mt_list = [MSVTransaction(mh, bank_code=10, bank_branch_code=9, bank_account_number=12345678, payee_tz=2198181,
                              payee_name="יהושע וייץ", payment_amount=2500.32, payee_institution_identifier='000002572'),

               MSVTransaction(mh, bank_code=10, bank_branch_code=9, bank_account_number=12345688, payee_tz=122198181,
                              payee_name="אבישי סביר", payment_amount=5000.54, payee_institution_identifier='000002573')
               ]

    mf = MSVFile(mh, mt_list)
    mf.dump()
