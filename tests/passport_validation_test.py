import numpy as np
import pandas as pd
from school_manager.routes.validation_country_passport_id import passport_id_validation
from school_manager.routes import validation_country_passport_id

# Import csv file fot tests and drop empty values.
# Notice!: need to replace the path of CSV file.
df_passport_id_success = pd.read_csv(r'C:\Users\qndlq\OneDrive\שולחן העבודה\דרכונים תקינים עם קוד מדינה לבדיקה.csv')
df_passport_id_success['country code'].replace(' ', np.nan, inplace=True)
df_passport_id_success.dropna(subset=['country code'], inplace=True)

# Creating lists with all the passport numbers and all the country code
country_code_success = df_passport_id_success[['country code']]
country_code_success = country_code_success['country code'].tolist()
passport_number_success = df_passport_id_success[['Passport Country']]
passport_number_success = passport_number_success['Passport Country'].tolist()

regex_index = 0
counter_test = 0
for i in range(len(country_code_success)):
    result = passport_id_validation(passport_number_success[i],
                                    validation_country_passport_id.country_regex_dictionary[country_code_success[i]][
                                        regex_index])
    if not result:
        print('passport id : ' + passport_number_success[i] + ' country code : ' + country_code_success[i])
    else:
        print(result)
    counter_test += 1

print('Count of tests : ' + str(counter_test))
