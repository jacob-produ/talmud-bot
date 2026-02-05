import re
import uuid
import tempfile
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By
import school_manager.constants.talmud as tc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from school_manager.modules.talmud .utils.log import Log
from selenium.webdriver.support import expected_conditions as ec
import school_manager.modules.talmud.utils.chrome_utils as c_utils
from selenium.webdriver.chrome.service import Service as ChromeService


# noinspection SpellCheckingInspection
class ExtractStudentsInfo:
    def __init__(self, talmud):
        self.driver = None
        self.username = talmud.username
        self.password = talmud.password
        self.current_branch = talmud.branch
        self.user_data_dir = tempfile.mkdtemp(prefix=f"chrome_{uuid.uuid4()}_")

    def perform(self):
        Log.log_message(tc.LABEL_INFO, tc.DEPARTURE_START, True)
        self.handle_students_group()
        Log.log_message(tc.LABEL_INFO, tc.DEPARTURE_END, True)

    def handle_students_group(self):

        # Perform login to get cookies and viewstate_key
        self.driver, session_cookies, viewstate_key = self.selenium_login(self.current_branch)
        self.get_students_info(self.driver, viewstate_key)
        # Check if login was successful
        if not session_cookies or not viewstate_key:
            Log.log_message(tc.LABEL_ERROR, tc.CREDENTIALS_ERROR, True)
            return

    def selenium_login(self, branch):
        self.driver = c_utils.get_chrome_driver(self.user_data_dir)
        success = c_utils.perform_login(self.driver, self.username, self.password)
        if success:
            try:
                # Get cookies from the driver
                cookies = self.driver.get_cookies()
                session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

                # Wait until the element with the specific class and title is present and clickable
                branch_tab = WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.XPATH, f"//a[contains(@class, 'ucTalmudSideBar_tvTalmud') and @title='{branch}']")))
                # Click on the element
                branch_tab.click()

                mosad_students_tab = WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, "__tab_ContentPlaceHolder1_tabInstituteDetails_TabPanel1")))
                mosad_students_tab.click()

                search_students_btn = WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_btnSearch")))
                # Click on the element
                search_students_btn.click()

                WebDriverWait(self.driver, 120).until(ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_lblCountSearch")))

                # Parse the response content with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                viewstate_key = soup.find('input', {'name': '__VIEWSTATE_KEY'}).get('value', '')

                Log.log_message(tc.LABEL_INFO, tc.SELENIUM_LOGIN_SUCCESS)
                return self.driver, session_cookies, viewstate_key

            except Exception as e:
                import traceback
                traceback.print_exc()
                Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
                Log.log_message(tc.LABEL_ERROR, e)
            finally:
                pass
        return None, None, None

    # noinspection PyArgumentList,HttpUrlsUsage
    @staticmethod
    def get_chrome_driver():
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
        chrome_options.add_argument("--allow-insecure-localhost")

        chrome_driver_service = ChromeService(ChromeDriverManager().install())

        # Set up the Burp Suite proxy
        if tc.PROXY_ENABLED:
            proxy = tc.PROXY_SERVER.replace("http://","")  # Replace it with your Burp Suite proxy address and port
            chrome_options.add_argument(f"--proxy-server={proxy}")

        driver = webdriver.Chrome(options=chrome_options, service=chrome_driver_service)

        return driver

    def get_students_info(self, cookies, viewstate_key):
        # ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_gvIStudents

        # Locate the table
        table = WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((By.CLASS_NAME, "GridTable")))

        # Find all rows in the table
        rows = table.find_elements(By.TAG_NAME, "tr")

        table_locator = (By.CLASS_NAME, "GridTable")
        row_locator = (By.TAG_NAME, "tr")
        textarea_locator = (By.NAME, "ctl00$ContentPlaceHolder1$txtBodyMsg")

        url = "https://talmud.edu.gov.il/Institutes/InstitutesDetails.aspx"
        headers = tc.HEADERS.copy()
        headers.update({
            "Referer": url,
        })

        # Payload dictionary with URL decoded values
        payload = {
            "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$UpdatePanelUpdate|ctl00$ContentPlaceHolder1$btnUpdateValueInTab3",
            "ContentPlaceHolder1_tabInstituteDetails_ClientState": '{"ActiveTabIndex":3,"TabState":[true,true,true,true,true]}',
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidIsPostBack": "1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidReturak": "0",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$txtSupportStartDate$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$txtInsManagerName": "הרב יהושע ברכץ",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$StudentsQuotaOld": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hIsValidInsMerchava": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidReplaceMap": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidAddAddress": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$ddlCity": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$ddlStreet": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$HouseNumber": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$ZipCode": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$POB": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$AddressStataus": "1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$txtContactNameAddress": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucAddressInstitutesInsertUpdate$txtComment": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucPhone$PhoneNumber": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucPhone$txtContactNamePhone": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucPhone$hidAreaCodes": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucPhone$hidCommTypes": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$txtFirstName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$txtLastName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$txtUserName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$txtEmail": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$hidCancelNewUser": "0",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$ucInsertNewUser$HidCheckUserName": "0",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidPhoneID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidAddressID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$HdnListCommunicationType": "1,4",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$HdnPhoneUpdateID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$UploadDocument1$hidFromPage": "InstitutesDetails",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$UploadDocument1$hidFileName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsDetails1$ucInstitutesDetails$hidInstID": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsStudyTypes$ucStudyTypeSearch$hidInstituteID": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsStudyTypes$ucStudyTypeSearch$hidStudyTypeID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsStudyTypes$ucStudyTypeSearch$hidInstituteStudyTypeID": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$InsStudyTypes$ucStudyTypeSearch$hidStudyTypeShow": "1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabInstituteEntitlement$ucInstituteEntitlementDetails$hidReport": "0",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabInstituteEntitlement$ucInstituteEntitlementDetails$ddlMonth": "01/06/2025",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hidStudents": "7",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hdnRetro": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hdnStudentChecked": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hidPopStudent": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlIdentificationTypeStudent": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$txtStudenPassport": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$txtFirstName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$txtLastName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$txtAssociationName": "עץ חיים ליוצאי צרפת",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlTransferApprovalStatusID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlStudyTypeID": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlStudentStatus": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlStudentsEntitlementStatus": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlStudentsIsInQuota": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlBirthDateSearch$txtDate": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlBirthDateSearch$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$UploadDocument1$hidFromPage": "InstitutesDetails",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$UploadDocument1$hidFileName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentClose$txtAssociationNamePU": "עץ חיים ליוצאי צרפת",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentClose$ctlLeaveDate$txtDate": "11/06/2025",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentClose$ctlLeaveDate$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentClose$hIsValidAssNum": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentClose$ddlLeaveReason": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlPopIdentityType": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ddlCountryOfOrigine": "-1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$txtIdentifier": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlBirthDate$txtDate": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlBirthDate$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlAcceptanceDate$txtDate": "11/06/2025",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ctlAcceptanceDate$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hidIsExistInAnothrStudyTypeInInstitute": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hidPerformTransfer": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$hidThisInstRecCount": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$HiddenGrid": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$cldFileDate$txtDate": "11/06/2025",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$cldFileDate$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$hidFromPage": "InstitutesDetails",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$hidFileName": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$hidCheckFileDate": "0",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$ucStudentFromExcel$hidRecognitionDate": "27/12/2006",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabPanel1$ucStudentsSearch$SearchCollapse_ClientState": "false",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$cblStatus$0": "1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$cblStatus$1": "2",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$cblStatus$2": "3",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ddlYear": "2025",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl02$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl03$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl04$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl05$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl06$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl07$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl08$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$gvInsDayOff$ctl09$hidStatus": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$hidAreYouSure": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ddlDayOffReason": "1",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ctlDayOffDateFrom$txtDate": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ctlDayOffDateFrom$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ctlDayOffDateTo$txtDate": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$ctlDayOffDateTo$MaskedEditExtender5_ClientState": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$txtComments": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$txtAgafComments": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$hidDayOffID": "",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$hidPartialPermitted": "1,2,3,",
            "ctl00$$ContentPlaceHolder1$tabInstituteDetails$TabDayOff$ucInstituteDayOff$hidRangePermitted": "2,3,",
            "ctl00$$ContentPlaceHolder1$hdnTabIndex": "3",
            "ctl00$$ContentPlaceHolder1$hdnLastTabIndex": "0",
            "ctl00$$ContentPlaceHolder1$hdnWhichButtonClick": "",
            "ctl00$$ContentPlaceHolder1$hdnTestChange": "1",
            "ctl00$$ucTalmudSideBar$hdnNode": "fff",
            "ctl00$$hiUserName": "",
            "ctl00$$hidActivityProofRemovePrevious": "",
            "ctl00$$hidActivityProofInstID": "",
            "__EVENTTARGET": "ctl00$$ContentPlaceHolder1$btnUpdateValueInTab3",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE_KEY": viewstate_key,
            "__VIEWSTATE": "",
            "__VIEWSTATEENCRYPTED": "",
            "__ASYNCPOST": "true"}

        # Make the POST request
        response = self.send_request(url, headers=tc.HEADERS, cookies=cookies, data=payload)
        print(response)
        # Check response status
        return None

    @staticmethod
    def send_request(url, headers, cookies, data):
        if tc.PROXY_ENABLED:
            response = requests.post(url, headers=headers, cookies=cookies, data=data, proxies=tc.PROXIES, verify=False)
        else:
            response = requests.post(url, headers=headers, cookies=cookies, data=data)
        return response

    @staticmethod
    def get_viewstate_key(response_text):
        # Parse the response content with BeautifulSoup
        match = re.search(r"\|__VIEWSTATE_KEY\|(VIEWSTATE_.*?)\|", response_text)

        if match:
            viewstate_key = match.group(1)  # Extract the value inside the pattern
            return viewstate_key
        else:
            Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_VIEWKEY_FAIL)
            return None
