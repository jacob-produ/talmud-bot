import dateparser

dates_to_parse = ["06/2020",
                  "06.2020",
                  "6.20",
                  "6/20",
                  "01/06/2020",
                  "01.06.2020",
                  "יונ-20"]
for date in dates_to_parse:
    parsed_date = dateparser.parse(date, languages=['he'], settings={'DATE_ORDER': 'YMD',
                                                                     'PREFER_DAY_OF_MONTH': 'first'})
    print(f"{date} -> {parsed_date}")