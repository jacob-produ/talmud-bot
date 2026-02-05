from __future__ import print_function
from os import path
import os.path
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DIR_PATH = path.dirname(__file__)
SERVICE_ACCOUNT_FILE = path.join(DIR_PATH,'school-manager.json')

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID and range of a sample spreadsheet.
IMPORT_SAMPLE_SPREADSHEET_ID = '1xDJA_fiHn5fapW2dwREqCmtH5jHUoapa-TDMXfpHmyc'
EXPORT_SAMPLE_SPREADSHEET_ID = '1vHANGT94TWyCy94s2vp5lHlOPnrf8PqI_5LTxU-JZr4'

def get_google_sheet_data(sheet_name, sheet_num_of_rows=1000, sheet_num_of_columns='Z'):

    try:
        service = build('sheets', 'v4', credentials=credentials)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=IMPORT_SAMPLE_SPREADSHEET_ID,
                                    range=f"{sheet_name}!A1:{sheet_num_of_rows}").execute()
        values = result.get('values', [])
        print(values[0])
        sheet_df = pd.DataFrame(values[1:], columns=values[0])
        values = sheet_df.to_dict(orient='records')
        if not values:
            print('No data found.')
            return
        print(values)
        return values
    except HttpError as err:
        print(err)

def post_google_sheet_data(table_name, data):
    sheet_name = 'export_test'
    try:
        service = build('sheets', 'v4', credentials=credentials)
        data = [row for row in data if len(row) >0]
        data_df = pd.DataFrame.from_dict(data)
        values = data_df.values.tolist()
        values.insert(0,data_df.columns.to_list())
        # [START_EXCLUDE silent]
        body = {

            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=IMPORT_SAMPLE_SPREADSHEET_ID, range=f"{sheet_name}!A1:100",
            valueInputOption='USER_ENTERED', body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


if __name__ == '__main__':

    data = [
        {"A":1,"B":423,"C":465},
        {"A": 2, "B": 654, "C": 423},
        {"A": 15, "B": 86, "C": 543},
        {"A": 6541, "B": 43, "C": 24},
    ]

    post_google_sheet_data('12',data)