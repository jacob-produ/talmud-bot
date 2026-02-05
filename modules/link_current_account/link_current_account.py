import re
from core import messages
import school_manager.models
from school_manager.models.expense import Expense
from school_manager.models.income import Income
from school_manager.models.income_source import IncomeSource, DEFAULT_CURRENT_ACCOUNT_IS
from school_manager.constants import constants, constants_lists
from school_manager.modules import exceptions


class LinkCurrentAccount:
    DEFAULT_CURRENT_ACCOUNT_IS_ID = None

    @classmethod
    def link_facade(cls, current_account_record, fk_institution_id):
        ca_results = []
        cls.DEFAULT_CURRENT_ACCOUNT_IS_ID = cls.get_default_income_source().get('id', None)

        del current_account_record['bank_account']
        del current_account_record['expense']
        del current_account_record['income']

        case = LinkCurrentAccount.find_link(current_account_record['transaction_description'])

        case_method, case_payment_method = case[0], case[1]
        link_current_account = case_method(**current_account_record, fk_institution_id=fk_institution_id,
                                           fk_current_account_id=current_account_record["id"],
                                           payment_method=case_payment_method)
        current_account_record["link"] = link_current_account

        if link_current_account[constants.STR_ERROR]:
            exceptions.LinkCurrentAccountError(message=link_current_account[constants.STR_MESSAGE])

        is_linked_update = school_manager.models.CurrentAccount.update({"is_linked": True},
                                                                       id=current_account_record[
                                                                           "id"])
        if is_linked_update[constants.STR_ERROR]:
            exceptions.LinkCurrentAccountError(message=is_linked_update[constants.STR_MESSAGE])

    @classmethod
    def find_link(cls, description):
        for case, opt in LinkCACases.items():
            if re.search(opt["REGEX"], description):
                return [opt["METHOD"], opt["PAYMENT_METHOD"]]

        raise exceptions.LinkCurrentAccountError(message=messages.LINK_NO_CASE.format(description))

    @classmethod
    def create_expense(cls, object_data):
        return Expense.create(object_data=object_data)

    @classmethod
    def get_expense(cls, **kwargs):
        return Expense.read(**kwargs)

    @classmethod
    def create_income(cls, object_data):
        return Income.create(object_data=object_data)

    @classmethod
    def update_expense(cls, updated_values_dict, id):
        return Expense.update(updated_values_dict=updated_values_dict, id=id)

    @classmethod
    def get_default_income_source(cls):
        return IncomeSource.read(many=False, name=DEFAULT_CURRENT_ACCOUNT_IS.get('name', ''))

    @classmethod
    def fee(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_expense({
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "payment_method": kwargs['payment_method'],
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
        })

    @classmethod
    def draw_check(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        check_number = int(re.search("\d+", kwargs['transaction_description']).group(0))
        result = cls.get_expense(check_number=check_number)

        if result is None or len(result) == 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_NO_CHECK_ERROR.format(check_number))

        elif len(result) == 1:
            return cls.update_expense({
                'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
                'fk_current_account_id': kwargs['fk_current_account_id']
            },
                id=result[0]['id'])

        elif result[-1]['payment_status'] == constants_lists.EXPENSE_PAYMENT_STATUS[4]:
            return cls.create_expense({
                "actual_payment_date": kwargs['date'],
                "fk_current_account_id": kwargs['fk_current_account_id'],
                "fk_bank_account_id": kwargs['fk_bank_account_id'],
                "fk_institution_id": kwargs['fk_institution_id'],
                "amount": abs(kwargs['transaction_amount']),
                'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
                "payment_method": kwargs['payment_method']
            })

        else:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_CHECK_CASE_ERROR.format(check_number))

    @classmethod
    def create_check(cls, **kwargs):
        if kwargs['transaction_amount'] < 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Positive"))

        check_number = int(re.search("\d+", kwargs['transaction_description']).group(0))
        result = cls.get_expense(check_number=check_number)
        if result is None or len(result) == 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_NO_CHECK_ERROR.format(check_number))

        new_check_data = {
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[4],
            "payment_method": kwargs['payment_method']
        }

        return cls.create_expense({**result[0], **new_check_data})

    @classmethod
    def ordinance_payment(cls, **kwargs):
        if kwargs['transaction_amount'] < 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Positive"))

        return cls.create_income({
            "deposit_date": kwargs['date'],
            "for_month": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "method": kwargs['payment_method'],
            "fk_income_source_id": cls.DEFAULT_CURRENT_ACCOUNT_IS_ID
        })

    @classmethod
    def social_security_charge(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_expense({
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "payment_method": kwargs['payment_method'],
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
        })

    @classmethod
    def mandatory_interest(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_expense({
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "payment_method": kwargs['payment_method'],
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
        })

    @classmethod
    def iec_charge(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_expense({
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "payment_method": kwargs['payment_method'],
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
        })

    @classmethod
    def deposit_check(cls, **kwargs):
        if kwargs['transaction_amount'] < 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Positive"))

        return cls.create_income({
            "deposit_date": kwargs['date'],
            "for_month": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "method": kwargs['payment_method'],
            "fk_income_source_id": cls.DEFAULT_CURRENT_ACCOUNT_IS_ID
        })

    @classmethod
    def receipt_institution(cls, **kwargs):
        if kwargs['transaction_amount'] < 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_income({
            "deposit_date": kwargs['date'],
            "for_month": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "method": kwargs['payment_method'],
            "fk_income_source_id": cls.DEFAULT_CURRENT_ACCOUNT_IS_ID
        })

    @classmethod
    def transfer(cls, **kwargs):
        if kwargs['transaction_amount'] > 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Positive"))

        return cls.create_expense({
            "actual_payment_date": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "payment_method": kwargs['payment_method'],
            'payment_status': constants_lists.EXPENSE_PAYMENT_STATUS[3],
        })

    @classmethod
    def transfer_from(cls, **kwargs):
        if kwargs['transaction_amount'] < 0:
            raise exceptions.LinkCurrentAccountError(message=messages.LINK_WRONG_AMOUNT_MESSAGE.format("Negative"))

        return cls.create_income({
            "deposit_date": kwargs['date'],
            "for_month": kwargs['date'],
            "fk_current_account_id": kwargs['fk_current_account_id'],
            "fk_bank_account_id": kwargs['fk_bank_account_id'],
            "fk_institution_id": kwargs['fk_institution_id'],
            "amount": abs(kwargs['transaction_amount']),
            "method": kwargs['payment_method'],
            "fk_income_source_id": cls.DEFAULT_CURRENT_ACCOUNT_IS_ID
        })


LinkCACases = {
    "FEE": {
        "REGEX": "(^עמלה|^עמלת)",
        "METHOD": LinkCurrentAccount.fee,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[2]
    }, "DRAW_CHECK": {
        "REGEX": "(^משיכה|^משיכת) שיק",
        "METHOD": LinkCurrentAccount.draw_check,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[0]
    }, "CREATE_CHECK": {
        "REGEX": "^הח שיק",
        "METHOD": LinkCurrentAccount.create_check,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[0]
    }, "ORDINANCE_PAYMENT": {
        "REGEX": "^פקודת תשלום",
        "METHOD": LinkCurrentAccount.ordinance_payment,
        "PAYMENT_METHOD": constants_lists.INCOME_PAYMENT_METHODS[5]
    }, "MANDATORY_INTEREST": {
        "REGEX": "(רבית|ריבית) חובה",
        "METHOD": LinkCurrentAccount.mandatory_interest,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[2]
    }, "SOCIAL_SECURITY_CHARGE": {
        "REGEX": "^חיוב ביטוח לאומ",
        "METHOD": LinkCurrentAccount.social_security_charge,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[2]
    }, "IEC_CHARGE": {
        "REGEX": "חברת (החשמל|חשמל)",
        "METHOD": LinkCurrentAccount.iec_charge,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[2]
    }, "DEPOSIT_CHECK": {
        "REGEX": "^הפקדת שיק",
        "METHOD": LinkCurrentAccount.deposit_check,
        "PAYMENT_METHOD": constants_lists.INCOME_PAYMENT_METHODS[0]
    }, "RECEIPT_INSTITUTION": {
        "REGEX": "^תקבול מוסד",
        "METHOD": LinkCurrentAccount.receipt_institution,
        "PAYMENT_METHOD": constants_lists.INCOME_PAYMENT_METHODS[2]
    }, "TRANSFER": {
        "REGEX": "^העברה-",
        "METHOD": LinkCurrentAccount.transfer,
        "PAYMENT_METHOD": constants_lists.EXPENSE_PAYMENT_METHODS[4]
    }, "TRANSFER_FROM": {
        "REGEX": "^העברה מ",
        "METHOD": LinkCurrentAccount.transfer_from,
        "PAYMENT_METHOD": constants_lists.INCOME_PAYMENT_METHODS[5]
    },
}
