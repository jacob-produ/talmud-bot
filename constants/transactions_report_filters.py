from school_manager.models.income import Income
from school_manager.models.income_source import IncomeSource
from school_manager.models.expense import Expense
from  school_manager.constants.constants_lists import ATTRIBUTIONS
from school_manager.constants.constants_lists import EXPENSE_PAYMENT_METHODS, EXPENSE_PAYMENT_STATUS, \
    INCOME_PAYMENT_METHODS
from school_manager.db import db
from sqlalchemy.sql import func
from sqlalchemy import or_, and_
import datetime



ATTRIBUTION_HEB_ENG = {
    "תלמידים": "student",
    "עובדים": "employee",
    "ספקים": "supplier",
    "ללא שיוך": None,
}


ATTRIBUTION_ENG_HEB = {
    "student": "תלמיד",
    "employee": "עובד",
    "supplier": "ספק",
    "without": "ללא שיוך"
}

FILTERS = [
    {"title": "תאריכים", "filters": [
        {"display_name": "תאריך יצירת הכנסה",
         "name": "income_date",
         "filter_key": "income_filters"},
        {"display_name": "תאריך יצירת הוצאה",
         "name": "expense_date",
         "filter_key": "expense_filters"},
    ], "name": "date_filters"},

    {"title": "הוצאות",
     "filters": [
         {"display_name": "סטטוס תשלום",
          "name": "expense_payment_status",
          "checkboxes": [*EXPENSE_PAYMENT_STATUS]},
         {"display_name": "צורת תשלום",
          "name": "expense_payment_method",
          "checkboxes": [*EXPENSE_PAYMENT_METHODS]},
     ],
     "name": "expense_filters"},
    {"title": "הכנסות", "filters": [
        {"display_name": "צורת הכנסה",
         "name": "income_payment_method",
         "checkboxes": [*INCOME_PAYMENT_METHODS]},
        {"display_name": "סוג מקור הכנסה",
         "name": "income_source",
         "checkboxes": ["שכר לימוד", "תרומות", "תקצוב עירוני", "תקצוב ממשלתי", "זמני"]},
    ], "name": "income_filters"},

    {"title": "שיוך",
     "filters": [
         {"display_name": "",
          "name": "attribution_type",
          "checkboxes": [*ATTRIBUTION_HEB_ENG]
          }],
     "name": "attribution_filters"},
]


def get_filter_query(filter_name, checked_list):
    switcher = {
        "expense_payment_status": Expense.payment_status.in_(checked_list),
        "expense_payment_method": Expense.payment_method.in_(checked_list),
        "income_payment_method": Income.method.in_(checked_list),
        "income_source": IncomeSource.type.in_(checked_list),
        # "expense_attribution": Expense.attribution.in_(checked_list),
        # "expense_attribution_id": Expense.attribution_id.in_(tuple(checked_list)),
        # "income_attribution": Income.attribution.in_(checked_list),
        # "income_attribution_id": Income.attribution_id.in_(tuple(checked_list)),
    }

    if filter_name.endswith("date"):
        switcher.update({
            "expense_date": Expense.created_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
            "income_date": Income.created_date.between(
                *[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
        })
    if filter_name.endswith("attribution_filters"):
        model = Income if filter_name.startswith('income') else Expense
        filters = []
        for heb_attribution in checked_list:
            eng_attribution = ATTRIBUTION_HEB_ENG.get(heb_attribution)
            if not eng_attribution:
                attribution_filters = [getattr(model,f'fk_{attribution}_id').is_(None) for attribution in ATTRIBUTIONS]
            else:
                attribution_filters = [getattr(model, f'fk_{attribution}_id').is_(None) if attribution != eng_attribution  else
                                       getattr(model, f'fk_{attribution}_id').isnot(None)
                                       for attribution in ATTRIBUTIONS]
            filters.append(and_(*attribution_filters))
        switcher.update({
            filter_name: or_(*filters)
        })
    #     if filter_name.endswith("attribution_filters") and list(ATTRIBUTION_HEB_ENG.keys())[-1] in checked_list:
    #     switcher.update({
    #         "expense_attribution_filters": or_(
    #             Expense.attribution.in_([ATTRIBUTION_HEB_ENG.get(attribution, None) for attribution in checked_list]),
    #             Expense.attribution.is_(None)),
    #         "income_attribution_filters": or_(
    #             Income.attribution.in_([ATTRIBUTION_HEB_ENG.get(attribution, None) for attribution in checked_list]),
    #             Income.attribution.is_(None)),
    #     })
    # elif filter_name.endswith("attribution_filters"):
    #     switcher.update({
    #         "expense_attribution_filters": Expense.attribution.in_(
    #             [ATTRIBUTION_HEB_ENG.get(attribution, None) for attribution in checked_list]),
    #         "income_attribution_filters": Income.attribution.in_(
    #             [ATTRIBUTION_HEB_ENG.get(attribution, None) for attribution in checked_list])
    #     })

    # Return True is the filter was not found, cause the query to ignore that missing filter
    return switcher.get(filter_name, True)
