import re
import uuid
import shutil
import tempfile
from time import sleep
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import school_manager.constants.talmud as tc
from selenium.webdriver.support.ui import WebDriverWait
from school_manager.modules.talmud.utils.log import Log
from selenium.webdriver.support import expected_conditions as ec
import school_manager.modules.talmud.utils.chrome_utils as c_utils
from school_manager.modules.talmud.utils.progress import ProgressManager
from school_manager.constants.constants import STR_ERROR, STR_MESSAGE, STR_FILE_DATA


# noinspection DuplicatedCode
class ApproveStudents:

    def __init__(self, talmud, approve=True):
        self.approve = approve
        self.username = talmud.username
        self.password = talmud.password
        self.driver = None
        self.user_data_dir = tempfile.mkdtemp(prefix=f"chrome_{uuid.uuid4()}_")
        self.task_key = getattr(talmud, 'task_key', None)
        self.students_data = set()

        for index, row in talmud.data_df.iterrows():
            self.students_data.add(row[tc.STUDENT_ID_COL_NAME])

    def perform(self):
        try:
            Log.log_message(tc.LABEL_INFO, tc.TRANSFER_START)
            result = self._perform()
            Log.log_message(tc.LABEL_INFO, tc.TRANSFER_END)

            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return e

    def _perform(self):
        self.driver = c_utils.get_chrome_driver(self.user_data_dir)
        success = c_utils.perform_login(self.driver, self.username, self.password)

        if success:
            try:
                # Get cookies from the driver
                cookies = self.driver.get_cookies()
                session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

                # Locate the table
                table = WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((By.CLASS_NAME, "GridTable")))

                # Find all rows in the table
                rows = table.find_elements(By.TAG_NAME, "tr")

                table_locator = (By.CLASS_NAME, "GridTable")
                row_locator = (By.TAG_NAME, "tr")
                textarea_locator = (By.NAME, "ctl00$ContentPlaceHolder1$txtBodyMsg")

                id_pattern = r'\b(ת\.ז\.|דרכון)\s(\S+)'

                current_page = 1
                no_action_students = []

                proceed = True

                processed = 0

                try:
                    total_estimate = len(rows) if rows else 0
                except Exception:
                    total_estimate = 0

                while proceed:
                    # Get the table rows on the current page
                    table = WebDriverWait(self.driver, 20).until(
                        ec.presence_of_element_located(table_locator)
                    )

                    rows = table.find_elements(*row_locator)

                    button_to_click = "ContentPlaceHolder1_btnTransferApprove" if self.approve is True else "ContentPlaceHolder1_btnTransferDecline"

                    # Iterate through rows using their index
                    for index in range(1, len(rows)):
                        # Re-fetch the table and rows to ensure fresh references
                        table = WebDriverWait(self.driver, 20).until(ec.presence_of_element_located(table_locator))
                        rows = table.find_elements(*row_locator)

                        # Get the specific row by index
                        row = rows[index]

                        td_element = row.find_elements(By.TAG_NAME, "td")

                        # Check if the date is not expired, if so - stop running.
                        date = datetime.strptime(td_element[4].text, "%d/%m/%Y")

                        if datetime.now() >= date + timedelta(days=3):
                            proceed = False
                            break

                        # check if the row is relevant, if not - move to the next one.
                        if not td_element[3].text == "נשלחה":
                            continue

                        row.click()  # Perform the click action on the row

                        # Wait for the textarea to appear
                        textarea = WebDriverWait(self.driver, 10).until(
                            ec.presence_of_element_located(textarea_locator)
                        )

                        # Get the message from the textarea
                        message = textarea.get_attribute("value")
                        student_id = re.search(id_pattern, message).groups()[1]

                        if student_id not in self.students_data:
                            no_action_students.append(student_id)
                            continue

                        if button_to_click:
                            button = WebDriverWait(self.driver, 20).until(
                                ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnTransferApprove")))
                            button.click()
                            ok_button = WebDriverWait(self.driver, 20).until(
                                ec.element_to_be_clickable((By.ID, "ucMessagePopUp_spanBtnOk")))
                            ok_button.click()

                            msg = tc.TRANSFER_PERFORMED.format(student_id,
                                                               tc.TRANSFER_APPROVED if self.approve else tc.TRANSFER_DENIED)
                            Log.log_message(tc.LABEL_INFO, msg)

                        processed += 1
                        if self.task_key and total_estimate:
                            percent = int((processed / max(total_estimate, 1)) * 100)
                            ProgressManager.set_progress(self.task_key, percent)

                    try:
                        sleep(1)
                        # Try to find and click the "Next" button on the pager (if available)
                        next_button = WebDriverWait(self.driver, 20).until(
                            ec.element_to_be_clickable(
                                (By.XPATH, ".//a[contains(@class, 'ButtonCssClass') and text()='›']")))

                        next_button.click()
                        current_page += 1
                        # Wait for the table to reload after clicking "Next"
                        WebDriverWait(self.driver, 20).until(ec.staleness_of(table))  # Wait for the table to be stale
                        WebDriverWait(self.driver, 20).until(
                            ec.presence_of_element_located(table_locator))  # Wait for a new table
                    except Exception:
                        break  # Exit the loop if there are no more pages

                print(no_action_students)
                if no_action_students:
                    Log.log_message(tc.LABEL_INFO, tc.NO_ACTION_PERFORMED.format({', '.join(map(str, no_action_students))}))
                    return {STR_ERROR: False, STR_FILE_DATA: no_action_students}

                return {STR_ERROR: False, STR_MESSAGE: tc.TRANSFER_SUCCESS}

            except Exception as e:
                import traceback
                traceback.print_exc()
                Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
                Log.log_message(tc.LABEL_ERROR, e)
            finally:
                pass
        return {STR_ERROR: True, STR_MESSAGE: "משהו השתבש, אנא נסה שוב"}

    def __exit__(self, exc_type, exc_val, exc_tb):
        # סגירת הדפדפן אם נפתח
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        # מחיקת התיקייה
        if self.user_data_dir:
            shutil.rmtree(self.user_data_dir, ignore_errors=True)