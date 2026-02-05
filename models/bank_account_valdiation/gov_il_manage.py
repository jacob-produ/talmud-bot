import json
from datetime import datetime
import requests



class GovILManage:
    URL_LINK_GOV_IL_BANK_AND_BRANCH = 'https://data.gov.il/api/3/action/datastore_search?resource_id=1c5bc716-8210-4ec7-85be-92e6271955c2&limit=2000'
    MIN_BANK_COUNT = 15
    MIN_BRANCH_COUNT = 1000
    dict_of_branch_per_bank_code_gov_il = dict()
    # Assuming you have a class variable to store the last update date
    last_update_date = None

    @staticmethod
    def update_bank_and_branch_dict_from_gov_il():
        try:
            response_from_gov_il = requests.get(
                GovILManage.URL_LINK_GOV_IL_BANK_AND_BRANCH)  # response_from_gov_il = 200
            if response_from_gov_il.status_code == 200:
                branch_and_all_detail_list = json.loads(response_from_gov_il.content)["result"]["records"]

                # Initialize the dictionary
                bank_branches = {}

                # Iterate over the records
                for record in branch_and_all_detail_list:
                    bank_code = record["Bank_Code"]
                    branch_code = record["Branch_Code"]

                    # Check if bank_code already exists in the dictionary
                    if bank_code in bank_branches:
                        # If so, append branch_code to the list
                        bank_branches[bank_code].append(branch_code)
                    else:
                        # If not, create a new list with branch_code
                        bank_branches[bank_code] = [branch_code]

                response_from_validation_gov_il = GovILManage.gov_il_validation_checking(bank_branches)
                if response_from_validation_gov_il:
                    GovILManage.dict_of_branch_per_bank_code_gov_il = bank_branches.copy()
                    # Update the last update date to today
                    GovILManage.last_update_date = datetime.now()
                return GovILManage.dict_of_branch_per_bank_code_gov_il
            else:
                print("Failed to retrieve data from the URL.")
        except Exception as e:
            print("An error occurred:", e)

    @staticmethod
    def get_dict_of_branch_per_bank_code_gov_il():
        # Check if last update date is None or before today
        if GovILManage.last_update_date is None or GovILManage.last_update_date.date() < datetime.now().date():
            # Call the update function if the last update was before today
            GovILManage.update_bank_and_branch_dict_from_gov_il()
        return GovILManage.dict_of_branch_per_bank_code_gov_il

    @staticmethod
    def gov_il_validation_checking(bank_branches):
        bank_codes = list(bank_branches.keys())
        branches_codes = list(bank_branches.values())
        # Flatten the branch of branches
        flattened_branches = [branch for sublist in branches_codes for branch in sublist]

        # Get the count of all branches/banks together
        total_branch_count = len(flattened_branches)
        total_bank_count = len(bank_codes)

        if total_bank_count > GovILManage.MIN_BANK_COUNT:
            if total_branch_count > GovILManage.MIN_BRANCH_COUNT:
                return True
            else:
                return False
        else:
            return False


if __name__ == "__main__":
    # יצירת אובייקט מהמחלקה
    GovILManageClass = GovILManage()

    # קריאה לפונקציה באמצעות האובייקט
    print(GovILManageClass.update_bank_and_branch_dict_from_gov_il())

    GovILManage.get_dict_of_branch_per_bank_code_gov_il()
