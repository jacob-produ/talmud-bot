import sys
import urllib
import json
import smtplib
import logging
import pandas as pd
from flask import request, jsonify
from flask_restful import Resource
# from school_manager.models.validation_api_log import ValidationApiLog, create_logs_requests
from school_manager.models import ValidationApiLog
import datetime

from school_manager.models.bank_account_valdiation.gov_il_manage import GovILManage


# # Global Last update, URL link from Gov.il, list of branchs and banks detail, list of branchs and banks, list of banks:
# last_update_of_govil_banks_and_branchs_list = datetime.datetime(2022, 12, 3, 0, 0, 0)
# url_link_govil_bank_and_branch = 'https://data.gov.il/api/3/action/datastore_search?resource_' \
#                                  'id=1c5bc716-8210-4ec7-85be-92e6271955c2&limit=2000'
# snifim_global_var = list(json.loads(urllib.request.urlopen(url_link_govil_bank_and_branch).read())["result"]["records"])
# snifim_and_bank_local = [{'Bank_Code': d['Bank_Code'], 'Branch_Code': d['Branch_Code']}
#                          for d in snifim_global_var]
# list_of_bank_code = set([d['Bank_Code'] for d in snifim_global_var])
#
# # Create dict in the format: dict{Bank_Code1:[branch_code(1), branch_code(2)....],
# #                                 Bank_Code2:[branch_code(1), branch_code(2)....],...}
# dict_of_branch_per_bank_code = {}
#
#
# def create_dict_of_branchs_per_bank_code():
#     global dict_of_branch_per_bank_code
#     for num in list_of_bank_code:
#         list_of_branch = []
#         for item in snifim_and_bank_local:
#             if item['Bank_Code'] == num:
#                 list_of_branch.append(item['Branch_Code'])
#         dict_of_branch_per_bank_code[num] = list_of_branch
#
#
# create_dict_of_branchs_per_bank_code()


def legal_checks_on_bank_numbers_13(account_number, branch_number, bank_code):
    """
    The calculation function for BALAL group
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    branch_number = str(branch_number).zfill(3)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later

    # Checking for "Check digit==0"
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 8

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values numbers[0]--> before "-" numbers[1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 6] for i in range(0, len(account_number), 6)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number and Branch number
    if len(first_account_number) != 6 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 2 or second_account_number.isdigit() == False: return False
    if len(branch_number) != 3 or branch_number.isdigit() == False: return False

    # The calculation:
    if bank_code == "10" or bank_code == "13" or bank_code == "34":
        # The calculation of Branch number:
        sumOfBranch = (int(branch_number[0]) * 10) + (int(branch_number[1]) * 9) + (int(branch_number[2]) * 8)

        # The calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 7
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + sumOfBranch + int(second_account_number))
    else:
        return False

    # Return the answer if the account and branch number is legal
    if result % 100 == 90 or result % 100 == 70 or result % 100 == 72 or result % 100 == 60 or result % 100 == 20:
        return True
    return False


def legal_checks_on_bank_numbers_12_04(account_number, branch_number, bank_code):
    """
    The calculation function for YAHAV & HAPOALIM banks
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    branch_number = str(branch_number).zfill(3)
    bank_code = str(bank_code).zfill(2)

    # Checking for "Check digit==0"
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 6

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 5] for i in range(0, len(account_number), 5)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number and Branch number
    if len(first_account_number) != 5 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False
    if len(branch_number) != 3 or branch_number.isdigit() == False: return False

    # The calculation:
    if bank_code == "12" or bank_code == "04":
        # The calculation of Branch number:
        sumOfBranch = (int(branch_number[0]) * 9) + (int(branch_number[1]) * 8) + (int(branch_number[2]) * 7)

        # The calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 6
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + sumOfBranch + (int(second_account_number) * 1))
    else:
        return False

    # Return the answer if the account and bank code is legal
    if result % 11 == 0 or result % 11 == 2:
        return True
    if bank_code == "12" and (result % 11 == 4 or result % 11 == 6):
        return True
    return False


def legal_checks_on_bank_numbers_11_17(account_number, branch_number, bank_code):
    """
    The calculation function for DISCOUNT group
    :type account_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later

    # Checking for "Check digit==0"
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 9

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 8] for i in range(0, len(account_number), 8)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number
    if len(first_account_number) != 8 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False

    if bank_code == "11" or bank_code == "17":
        # The calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 9
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + (int(second_account_number) * 1))
    else:
        return False

    # Return the answer if the account number is legal
    if result % 11 == 0 or result % 11 == 2 or result % 11 == 4:
        return True
    return False


def legal_checks_on_bank_numbers_20(account_number, branch_number, bank_code):
    """
    The calculation function for MIZRAHI bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Any branch over 400 we subtract 400 and then continue to calculate.
    branch_number = str(branch_number)
    if len(branch_number) < 3 or branch_number.isdigit() == False: return False

    while 800 > int(branch_number) > 400:
        branch_number = int(branch_number) - 400
        print(branch_number)

    # Save the var that the function get as string (if they integers they will change to string)
    branch_number = str(branch_number).zfill(3)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later

    # Checking for "Check digit==0"
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 6

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 5] for i in range(0, len(account_number), 5)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number and Branch number
    if len(first_account_number) != 5 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False

    # The calculation:
    if bank_code == "20":
        # The calculation of Branch number:
        sumOfBranch = (int(branch_number[0]) * 9) + (int(branch_number[1]) * 8) + (int(branch_number[2]) * 7)

        # The calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 6
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + sumOfBranch + (int(second_account_number) * 1))
    else:
        return False

    # Return the answer if the account number is legal
    if result % 11 == 0 or result % 11 == 2 or result % 11 == 4:
        return True
    return False


def legal_checks_on_bank_numbers_31_52(account_number, branch_number, bank_code):
    """
    The calculation function for BINLEOMI group
    :type account_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # save the var that the function get as string (if they integers they will change to string)
    account_number = str(account_number)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 9

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 8] for i in range(0, len(account_number), 8)]

    # save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # validation account number
    if len(first_account_number) != 8 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False

    if bank_code == "31" or bank_code == "52":
        # the calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 9
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + (int(second_account_number) * 1))
    else:
        return False

    # return the answer if the account number is legal
    if result % 11 == 0 or result % 11 == 6:
        return True
    else:
        first_account_number_level_2 = first_account_number[3:]
        # the  level 2 calculation of Account number:
        sum_of_first_account_number_level_2 = 0
        coefficient_level_2 = 6
        for i in range(len(first_account_number_level_2)):
            sum_of_first_account_number_level_2 += int(first_account_number_level_2[i]) * coefficient_level_2
            coefficient_level_2 -= 1

        # calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number_level_2 + (int(second_account_number) * 1))

        # return the answer if the account number is legal
        if result % 11 == 0 or result % 11 == 6: return True
    return False


def legal_checks_on_bank_numbers_09(account_number, branch_number, bank_code):
    """
    The calculation function for DOAR bank
    :type account_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    account_number = str(account_number)  # bank code will save with zero fill to 9 chars if is less than 1
    # digit
    bank_code = str(bank_code).zfill(2)  # bank code will save with zero fill to 2 chars if is int(1 digit)

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 9

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 8] for i in range(0, len(account_number), 8)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number
    if len(first_account_number) != 8 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False

    if bank_code == "09":
        # The calculation of Account number:
        sum_of_first_account_number = 0
        coefficient = 9
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + (int(second_account_number) * 1))
    else:
        return False

    # Return the answer if the account and branch number is legal
    if result % 10 == 0:
        return True
    return False


def legal_checks_on_bank_numbers_22(account_number, branch_number, bank_code):
    """
    The calculation function for CITIBANK bank
    :type account_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    account_number = str(account_number)  # we don't need to zero fill here because the number should be exactly 9
    # digits.
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 9

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 8] for i in range(0, len(account_number), 8)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number
    if len(first_account_number) != 8 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False

    if bank_code == "22":
        # The calculation of Account number:
        the_sum_of_first_digits_in_first_account_number = (int(first_account_number[0]) * 3) + (
                int(first_account_number[1]) * 2)
        sum_of_first_account_number = 0
        coefficient = 7
        first_account_number = first_account_number[2:]

        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = sum_of_first_account_number + the_sum_of_first_digits_in_first_account_number
    else:
        return False

    # Return the answer if the account number and bank code is legal
    if str(11 - (result % 11)) == second_account_number:
        return True
    else:
        return False


def legal_checks_on_bank_numbers_46(account_number, branch_number, bank_code):
    """
    The calculation function for MASAD bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    account_number = str(account_number)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later
    branch_number = str(branch_number).zfill(3)

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 6

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 5] for i in range(0, len(account_number), 5)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number and branch number
    if len(first_account_number) != 5 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False
    if len(branch_number) != 3 or branch_number.isdigit() == False: return False

    if bank_code == "46":
        # The calculation of Account number:
        sumOfBranch = (int(branch_number[0]) * 9) + (int(branch_number[1]) * 8) + (int(branch_number[2]) * 7)
        sum_of_first_account_number = 0
        coefficient = 6
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + (int(second_account_number) * 1) + sumOfBranch)
    else:
        return False

    # Return the answer if the account and branch number is legal
    if result % 11 == 0:
        return True
    if result % 11 == 2:
        # Check all the branch number that modulo 2 is approved
        if branch_number == "192" or branch_number == "191" or branch_number == "183" or branch_number == "181" or \
                branch_number == "178" or branch_number == "166" or branch_number == "154" or branch_number == "539" or \
                branch_number == "527" or branch_number == "516" or branch_number == "515" or branch_number == "507" or \
                branch_number == "505" or branch_number == "503": return True

    else:
        # The  level 2 calculation of Account number:
        sum_of_first_account_number_level_2 = 0
        coefficient_level_2 = 9
        for i in range(len(first_account_number)):
            sum_of_first_account_number_level_2 += int(first_account_number[i]) * coefficient_level_2
            coefficient_level_2 -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number_level_2 + (int(second_account_number) * 1))

        # Return the answer if the account and branch number is legal
        if result % 11 == 0:
            return True
        else:
            result = sum_of_first_account_number + (int(second_account_number) * 1)
            if result % 11 == 0:
                return True
            else:
                return False


def legal_checks_on_bank_numbers_14(account_number, branch_number, bank_code):
    """
    The calculation function for OTSAR HAHA-YAL bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Save the var that the function get as string (if they integers they will change to string)
    account_number = str(account_number)
    bank_code = str(bank_code)  # we don't need to zero fill here because of if check that be performed later
    branch_number = str(branch_number).zfill(3)

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 6

    if len(account_number) == max_len_account - 1:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Create a list with 2 values [0]--> before "-" [1]--> after "-"
    if "-" in account_number:
        numbers = account_number.split('-')
    else:
        numbers = [account_number[i:i + 5] for i in range(0, len(account_number), 5)]

    # Save var for digits before "-" and the number after "-"
    first_account_number = numbers[0]
    second_account_number = numbers[1]

    # Validation account number and branch number
    if len(first_account_number) != 5 or first_account_number.isdigit() == False: return False
    if len(second_account_number) != 1 or second_account_number.isdigit() == False: return False
    if len(branch_number) != 3 or branch_number.isdigit() == False: return False

    if bank_code == "14":
        # The calculation of Account number:
        sumOfBranch = (int(branch_number[0]) * 9) + (int(branch_number[1]) * 8) + (int(branch_number[2]) * 7)
        sum_of_first_account_number = 0
        coefficient = 6
        for i in range(len(first_account_number)):
            sum_of_first_account_number += int(first_account_number[i]) * coefficient
            coefficient -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number + (int(second_account_number) * 1) + sumOfBranch)
    else:
        return False

    # Return the answer if the account and branch number is legal
    if result % 11 == 0:
        return True
    if result % 11 == 2:
        # Check all the branch number that modulo 2 is approved
        if branch_number == "385" or branch_number == "384" or branch_number == "365" or branch_number == "347" or \
                branch_number == "361" or branch_number == "362" or branch_number == "363":
            return True
    if result % 11 == 4:
        # Check all the branch number that modulo 4 is approved
        if branch_number == "361" or branch_number == "362" or branch_number == "363":
            return True

    else:
        # The  level 2 calculation of Account number:
        sum_of_first_account_number_level_2 = 0
        coefficient_level_2 = 9
        for i in range(len(first_account_number)):
            sum_of_first_account_number_level_2 += int(first_account_number[i]) * coefficient_level_2
            coefficient_level_2 -= 1

        # Calculation of the Legal checks on account numbers
        result = (sum_of_first_account_number_level_2 + (int(second_account_number) * 1))

        # Return the answer if the account and branch number is legal
        if result % 11 == 0:
            return True
        else:
            # level 2 of test 2:
            result = sum_of_first_account_number + (int(second_account_number) * 1)
            if result % 11 == 0:
                return True
            else:
                return False


def legal_checks_on_bank_numbers_54(account_number, branch_number, bank_code):
    """
    The calculation function for Jerusalem bank - No rules for account number of Jerusalem bank-54
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Convert the account number to a string with zero filling to a length of 15
    account_number_str = str(account_number).zfill(15)

    # Check if the string contains only digits or a single hyphen
    if all(c.isdigit() or c == "-" for c in account_number_str):
        return True
    else:
        return False


def legal_checks_on_bank_numbers_23(account_number, branch_number, bank_code):
    """
    The calculation function for HSBC bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Convert account_number to string
    account_number = str(account_number)

    # Convert branch_number to string and pad with zeros until length is 3
    branch_number = str(branch_number).zfill(3)

    # Check if all characters in account_number and branch_number are digits or "-". If not, return False
    if not all(c.isdigit() or c == "-" for c in account_number + branch_number):
        return False

    # Checking for "Check digit==0"
    # Remove any hyphens from account_number
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 9

    if len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Check for branch_number = "101"
    if branch_number == "101":
        # Check if the digit in the 7th position of account_number is "4"
        if account_number[6] == "4":
            return True
        else:
            return False

    # Check for branch_number = "102"
    elif branch_number == "102":
        # Check if account_number ends with "001"
        if account_number[-3:] == "001":
            return True
        else:
            return False

    # If branch_number is neither "101" nor "102", return False
    else:
        return False


def legal_checks_on_bank_numbers_18(account_number, branch_number, bank_code):
    """
    The calculation function for One-Zero bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """

    # Check if the account number is 9 digits long and includes only digits
    # Check if the account number is 7 digits + 1 "-" character + 2 digits at the end
    if not len(account_number) == 9 and account_number.isdigit():
        if not ((len(account_number) == 10 and
                 account_number[-3] == "-" and
                 account_number[:-3].isdigit() and
                 account_number[-2:].isdigit()) or (len(account_number) == 9 and
                                                    account_number)):
            return False

    # Create a new string with the branch number at the beginning and the first 7 digits of the account number
    merge_branch_account = branch_number + account_number[:7]

    # Convert the new string to an integer
    merge_branch_account = int(merge_branch_account)

    # Calculate the modulo result
    modulo_result = merge_branch_account % 97

    # Check if 98 - modulo_result is equal to the last 2 digits of the account number
    if 98 - modulo_result == int(account_number[-2:]):
        return True
    else:
        return False


def legal_checks_on_bank_numbers_10_34(account_number, branch_number, bank_code):
    """
    The calculation function for BALAL-Group bank
    :type account_number: int / str
    :type branch_number: int / str
    :type bank_code: int / str
    :rtype: bool
    """
    # Check if account number includes any characters other than "-"
    if any(c.isalpha() for c in account_number if c != "-"):
        return False

    # Check if branch number is only digits
    if not branch_number.isdigit():
        return False

    # Checking for "Check digit==0"
    account_number = account_number.replace("-", "")
    first_character = str(account_number)[0]
    max_len_account = 8

    if len(account_number) < max_len_account:
        account_number = str(account_number).zfill(max_len_account)
    elif len(account_number) == max_len_account + 1 and first_character == "0":
        account_number = str(account_number)[1:]

    # Calculate result_calculation
    result_calculation = (int(branch_number[0]) * 10) + (int(branch_number[1]) * 9) + (int(branch_number[2]) * 8) + (
            int(account_number[0]) * 7) + (int(account_number[1]) * 6) + (int(account_number[2]) * 5) + (
                                 int(account_number[3]) * 4) + (int(account_number[4]) * 3) + (
                                 int(account_number[5]) * 2)

    # Calculate result_1, result_2, result_3, result_4
    result_1 = result_calculation + 128
    result_2 = result_calculation + 180
    result_3 = result_calculation + 330
    result_4 = result_calculation + 340

    branch_number = str(branch_number).zfill(3)

    # Calculate result_5 if the second and third digits of the account number are 7 or 8
    if branch_number == "800":
        if (account_number[1] in ["2", "0"]) and (account_number[2] in ["0", "3"]):
            result_5 = result_calculation + 110
            mod_5 = result_5 % 100
            if mod_5 == 0 and account_number[-2:] == "00":
                return True
            difference_5 = 100 - mod_5
            if difference_5 == int(account_number[-2:]):
                return True
    else:
        if (account_number[1] in ["0"]) and (account_number[2] in ["0"]):
            result_5 = result_calculation + 110
            mod_5 = result_5 % 100
            if mod_5 == 0 and account_number[-2:] == "00":
                return True
            difference_5 = 100 - mod_5
            if difference_5 == int(account_number[-2:]):
                return True

    # Calculate modulos
    mod_1 = result_1 % 100
    mod_2 = result_2 % 100
    mod_3 = result_3 % 100
    mod_4 = result_4 % 100

    # Check if modulo is equal to 0 and the last 2 digits of the account number are 0
    if (mod_1 == 0 and account_number[-2:] == "00") or (mod_2 == 0 and account_number[-2:] == "00") or (
            mod_3 == 0 and account_number[-2:] == "00") or (mod_4 == 0 and account_number[-2:] == "00"):
        return True

    # Calculate differences
    difference_1 = 100 - mod_1
    difference_2 = 100 - mod_2
    difference_3 = 100 - mod_3
    difference_4 = 100 - mod_4

    # Check if any of the differences equal the last 2 digits of the account number
    if difference_1 == int(account_number[-2:]) or difference_2 == int(account_number[-2:]) or difference_3 == int(
            account_number[-2:]) or difference_4 == int(account_number[-2:]):
        return True
    else:
        return False


def create_validation_response_json(message, error, data, status):
    response_json = {
        "message": message,
        "error": error,
        "data": data,
        "status": status
    }
    return response_json


def email_sending_update_id(message, subject):
    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.starttls()
    server.login('Fensive@outlook.com', 'F3n5iv3t35tin6')
    server.sendmail('SM-Alive checker <Fensive@outlook.com>', 'Fensive@outlook.com',
                    'Subject: ' + subject +
                    'message \n\n This is e-mail from python.' + message)
    # Add a log into the log.txt file [print('Mail sent')]
    logging.debug("'Mail sent...")


def check_records_in_country_website(bank_code, branch_number):
    try:
        gov_il_dictionary = GovILManage.get_dict_of_branch_per_bank_code_gov_il()

        # Condition file obj record if the response True-list object_to_find, if False-Empty list
        if int(branch_number) in gov_il_dictionary[int(bank_code)]:
            data_bank_record = [int(bank_code), int(branch_number)]
        else:
            data_bank_record = []
    except Exception as e:
        print("An error occurred:", e)
        data_bank_record = []

    branch_number = str(branch_number).zfill(3)
    bank_code = str(bank_code).zfill(2)

    if bank_code == "09" and branch_number == "001":
        data_bank_record = [
            {'Bank_Code': 9, 'Bank_Name': 'Bank HADOAR', 'Branch_Code': 1, 'Branch_Name': ' Branch number 1 ',
             'Address': ' Sderot Hareches 21', 'City': "Modieen", 'Zip_Code': 7178437, 'POB': 0,
             'Telephone': '02-5005303', 'Fax': '02-5005300', 'Free_Telephone': '076-8871133',
             'Handicap_Accessible': 'Yes', 'Day_Closed': 'Saturday', 'Open_Date': '1949-01-02T00:00:00',
             'Close_Date': None}]
    elif bank_code == "34":
        data_bank_record = [{'Bank_Code': 34, 'Bank_Name': 'Bank Arviay Israel',
                            'Branch_Code': "12,14,18,19,32,34",
                            'Branch_Name': ' Aksal,Aabalin,Boaeina,BeitJan,OmElFahem ',
                            'Address': ' Sderot Hareches 21', 'City': "Modieen", 'Zip_Code': 7178437, 'POB': 0,
                            'Telephone': '02-5005303', 'Fax': '02-5005300', 'Free_Telephone': '076-8871133',
                            'Handicap_Accessible': 'Yes', 'Day_Closed': 'Saturday', 'Open_Date': '1949-01-02T00:00:00',
                            'Close_Date': None}]
    return data_bank_record


# Ask for answer from the appropriate function
legal_check_dictionary = {
    "04": legal_checks_on_bank_numbers_12_04,
    "4": legal_checks_on_bank_numbers_12_04,
    "9": legal_checks_on_bank_numbers_09,
    "09": legal_checks_on_bank_numbers_09,
    "10": legal_checks_on_bank_numbers_10_34,
    "11": legal_checks_on_bank_numbers_11_17,
    "12": legal_checks_on_bank_numbers_12_04,
    "13": legal_checks_on_bank_numbers_13,
    "14": legal_checks_on_bank_numbers_14,
    "17": legal_checks_on_bank_numbers_11_17,
    "18": legal_checks_on_bank_numbers_18,
    "20": legal_checks_on_bank_numbers_20,
    "22": legal_checks_on_bank_numbers_22,
    "23": legal_checks_on_bank_numbers_23,
    "26": legal_checks_on_bank_numbers_14,  # U-bank with the beinleumi
    "31": legal_checks_on_bank_numbers_31_52,
    "34": legal_checks_on_bank_numbers_10_34,
    "46": legal_checks_on_bank_numbers_46,
    "52": legal_checks_on_bank_numbers_31_52,
    "54": legal_checks_on_bank_numbers_54,
}


class ValidationAccountAPI(Resource):
    def post(self):
        """
        handle data about the details of the bank account, and make a validation test
        :return: JSON answer
        """
        # Creating default variables that will return in JSON
        error = False
        data = None
        status = "failed"
        response_json = {}
        try:
            # user_json get: (dict)bank_inspection (Bank, Snif, Account), (str)api_password
            user_json = request.get_json()

            # Saving the values of specific key in a variable
            bank_inspection = user_json['bank_inspection']
            api_password = user_json['api_password']

            # Validation of the password and return if incorrect password
            if api_password != "fkhjas907412zxcl,nja7$%!#!":
                message = "The password is incorrect"
                error = True
            else:
                # Saving the values from specific key in a variable from bank inspection dictionary
                bank_code = str(bank_inspection["Bank"])
                branch_number = str(bank_inspection["Snif"])
                account_number = str(bank_inspection["Account"])

                # Check if bank_code, branch_number and account_number are empty
                if bank_code == '' and branch_number == '' and account_number == '':
                    message = "Skip - The bank code, branch number and account number are empty"
                    error = False
                    data = False
                    status = "success"
                else:
                    # Check if branch number belong to bank code and save the response
                    data_bank_record = check_records_in_country_website(bank_code, branch_number)

                    # if the response is Not belong create message and data=False, other continue
                    if not data_bank_record:
                        message = "פרטי חשבון הבנק שגויים" + " The bank code: " + bank_code + \
                                  " and branch number: " + branch_number + " do not belong to each other"
                        data = False

                    else:
                        if bank_code in legal_check_dictionary:
                            if legal_check_dictionary[bank_code](account_number, branch_number, bank_code):
                                message = "פרטי חשבון הבנק נכונים" + " The bank account details are correct - Bank code: " + bank_code + ", Account number: " + \
                                          account_number + ", Branch number: " + branch_number
                                status = "success"
                                data = True

                            else:
                                message = "פרטי חשבון הבנק שגויים" + " The bank account details are incorrect - Bank " \
                                                                     "code: " + bank_code + ", Account number: " + account_number + \
                                          ", Branch number: " + branch_number
                                data = False

                        else:
                            message = "The " + bank_code + " bank code doesn't exist"
                            error = True

                response_json = create_validation_response_json(message, error, data, status)
                jsonify(ValidationApiLog.create_logs_requests(response_json, user_json, "bank account"))
                print(response_json)

        except Exception as e:
            message = "Invalid input, Error message: " + str(e)
            error = True
            status = "success"
            response_json = create_validation_response_json(message, error, data, status)
        return response_json
