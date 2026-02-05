import datetime
import dateparser

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def get_retro_date(retro_months):
    today = datetime.datetime.today()
    if today.month > retro_months:
        return datetime.date(today.year,today.month - retro_months, 1)
    else:
        return datetime.date(today.year - 1, 12 + today.month - retro_months, 1)


def get_formatted_now_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')


def parse_date_from_str(date_str):
    # try:
    return dateparser.parse(date_str, languages=['he'], settings={'DATE_ORDER': 'YMD',
                                                                      'PREFER_DAY_OF_MONTH': 'first','TIMEZONE': '+0200'})
    # except Exception as e:
    #     return datetime.datetime(day=1,month=1,year=21)

