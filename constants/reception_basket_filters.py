import datetime
from school_manager.models.income import Income
from school_manager.models.periodic_reception import PeriodicReception
from school_manager.constants.constants_lists import PERIODIC_RECEPTION_METHODS,PERIODIC_RECEPTION_STATUS
RB_FILTERS = [
        {"title": "הכנסות",
         "filters": [
            {"display_name": "צורת תשלום",
             "name": "income_payment_method",
             "checkboxes": ["אשראי", "מסב"]},
         ],
         "name": "income_filters"},
    ]

PR_FILTERS = [
        {"title": "תאריכים",
            "filters": [
            {"display_name": "תאריך יצירת התקבול המחזורי",
             "name": "periodic_reception_create_date",
             "filter_key": "pr_filters"}],
        "name": "date_filters"
         },
        {
        "title": "תקבולים מחזוריים",
         "filters": [

            {"display_name": "צורת הכנסה",
             "name": "periodic_reception_payment_method",
             "checkboxes": [*PERIODIC_RECEPTION_METHODS]},
            {"display_name": "סטטוס תקבול",
             "name": "periodic_reception_status",
             "checkboxes": [*PERIODIC_RECEPTION_STATUS]},
            {"display_name": "פעיל",
             "name": "periodic_reception_active",
             "checkboxes": ["פעיל","לא פעיל"]},
         ],
         "name": "pr_filters"},
    ]



# Backend Filters
def get_filter_query(filter_name, checked_list):
    if filter_name == "periodic_reception_active":
        if checked_list[0] == "פעיל":
            return PeriodicReception.active == 1
        else:
            return PeriodicReception.active == 0
    switcher = {
        "income_payment_method": Income.method.in_(checked_list),
        "income_payment_status": Income.payment_status.in_(checked_list),
        "periodic_reception_payment_method": PeriodicReception.payment_method.in_(checked_list),
        "periodic_reception_status": PeriodicReception.periodic_reception_status.in_(checked_list),
        "periodic_reception_active": PeriodicReception.active.in_(checked_list),
    }
    if filter_name.endswith("date"):
        switcher.update({
            "periodic_reception_create_date": PeriodicReception.created_date.between(*[datetime.datetime.strptime(date, '%d/%m/%Y %H:%M') for date in checked_list]),
        })
    # Return True is the filter was not found, cause the query to ignore that missing filter
    return switcher.get(filter_name, True)