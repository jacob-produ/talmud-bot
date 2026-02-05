import time
import uuid
import numpy
import shutil
import tempfile
import traceback
import pandas as pd
import multiprocessing
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import school_manager.constants.talmud as tc
from school_manager.modules.talmud.utils.log import Log
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
import school_manager.modules.talmud.utils.chrome_utils as c_utils
from school_manager.modules.talmud.utils.results_file import ResultsFile
from school_manager.modules.talmud.utils.progress import ProgressManager
from school_manager.constants.constants import STR_ERROR, STR_MESSAGE, STR_FILE_DATA
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
    WebDriverException
)


# ============================================================
#   Utility: Thread-safe helpers for Selenium and shared dicts
# ============================================================

def safe_click(driver, locator, retries=3, wait_time=2):
    """Safely click an element with retries and waits."""
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, wait_time).until(ec.element_to_be_clickable(locator))
            element.click()
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, WebDriverException):
            if attempt == retries - 1:
                raise
            time.sleep(1)
    return False


def safe_select_by_value(select_element, value, fallback_text=None):
    """Select safely by value, fallback to visible text."""
    try:
        select_element.select_by_value(value)
    except NoSuchElementException:
        if fallback_text:
            select_element.select_by_visible_text(fallback_text)
        else:
            raise


def add_result(shared_dict, student_id, study_type, current_branch, departed, details):
    """Append a result into Manager().dict() safely."""
    shared_dict[tc.STUDENT_ID_COL_NAME].append(student_id)
    shared_dict[tc.STUDY_TYPE_COL_NAME].append(study_type)
    shared_dict[tc.BRANCH_COL_NAME].append(current_branch)
    shared_dict[tc.DEPARTED_COL_NAME].append(departed)
    shared_dict[tc.DETAILS_COL_NAME].append(details)


# ============================================================
#   Core: Remove Student Worker
# ============================================================

def remove_student_by_id_worker(student_id, study_type, driver, current_branch, shared_results, shared_failures):
    """Perform a full remove-student flow, stable under multiprocessing."""
    try:
        # בדיקה שה-driver תקין
        if not driver or not getattr(driver, "session_id", None):
            raise RuntimeError("Driver not initialized or invalid session")

        # שלב 1: הזנת ת.ז.
        id_input = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_txtStudenPassport"))
        )
        id_input.clear()
        id_input.send_keys(student_id)

        # שלב 2: בחירת סוג לימוד
        select_id_type = Select(WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_ddlStudyTypeID"))
        ))
        safe_select_by_value(select_id_type, str(study_type))

        # שלב 3: חיפוש תלמיד
        safe_click(driver, (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_btnSearch"))
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_gvIStudents"))
        )

        try:
            # שלב 4: בחירת תלמיד
            checkbox_locator = (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_gvIStudents_selectedStudent_0")
            safe_click(driver, checkbox_locator)
        except Exception:
            add_result(shared_results, student_id, study_type, current_branch, tc.RESULTS_FAILURE, tc.RESULTS_REASON_STUDENT_NOT_FOUND)
            add_result(shared_failures, student_id, study_type, current_branch, tc.RESULTS_FAILURE, tc.RESULTS_REASON_STUDENT_NOT_FOUND)
            return False

        # שלב 5: פתיחת חלון עזיבה
        safe_click(driver, (By.ID, "ContentPlaceHolder1_btnStudentDeparture3"))

        # שלב 6: המתנה לחלון וסיבת עזיבה
        modal_locator = (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_pnlCloseStudent")
        select_locator = (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_ucStudentClose_ddlLeaveReason")

        WebDriverWait(driver, 20).until(ec.visibility_of_element_located(modal_locator))
        select_el = WebDriverWait(driver, 15).until(ec.visibility_of_element_located(select_locator))
        select_reason = Select(select_el)
        safe_select_by_value(select_reason, "3", fallback_text="מעבר בין ישיבות")

        # שלב 7: אישור
        safe_click(driver, (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_ucStudentClose_btnDepartureStudent"))
        WebDriverWait(driver, 15).until(ec.invisibility_of_element_located(modal_locator))

        # שלב 8: שמירה
        safe_click(driver, (By.ID, "ContentPlaceHolder1_btnSaveTab3"))
        safe_click(driver, (By.ID, "ucMessagePopUp_spanBtnOk"))

        add_result(shared_results, student_id, study_type, current_branch, tc.RESULTS_SUCCESS, tc.RESULTS_SUCCESS_MESSAGE)
        return True

    except Exception as e:
        traceback.print_exc()
        err = str(e)[:200]
        add_result(shared_results, student_id, study_type, current_branch, tc.RESULTS_FAILURE,
                   f"{tc.RESULTS_REASON_DEPARTURE_STUDENT_FAILED} ({err})")
        add_result(shared_failures, student_id, study_type, current_branch, tc.RESULTS_FAILURE,
                   f"{tc.RESULTS_REASON_DEPARTURE_STUDENT_FAILED} ({err})")
        return False


# ============================================================
#   Selenium Login Worker
# ============================================================

def selenium_login_worker(branch, user_data_dir, username, password):
    """Perform login in isolated Chrome session."""
    driver = c_utils.get_chrome_driver(user_data_dir)
    try:
        success = c_utils.perform_login(driver, username, password)
        if not success:
            Log.log_message(tc.LABEL_ERROR, tc.CREDENTIALS_ERROR)
            driver.quit()
            return None, None, None

        cookies = driver.get_cookies()
        session_cookies = {c['name']: c['value'] for c in cookies}

        links = driver.find_element(By.ID, "ucTalmudSideBar_tvTalmudn0Nodes").find_elements(By.TAG_NAME, "a")
        branch_found = False
        for link in links:
            if f"{branch}" == link.accessible_name:
                link.click()
                branch_found = True
                break
        if not branch_found:
            Log.log_message(tc.LABEL_ERROR, tc.ADD_BRANCH_NOT_FOUND.format(branch))
            driver.quit()
            return None, None, None

        # טעינת לשונית תלמידים
        WebDriverWait(driver, 30).until(ec.element_to_be_clickable(
            (By.ID, "__tab_ContentPlaceHolder1_tabInstituteDetails_TabPanel1")
        )).click()
        WebDriverWait(driver, 30).until(ec.presence_of_element_located(
            (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_btnSearch")
        )).click()

        WebDriverWait(driver, 120).until(ec.presence_of_element_located(
            (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_lblCountSearch")
        ))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        viewstate_key = soup.find('input', {'name': '__VIEWSTATE_KEY'}).get('value', '')

        Log.log_message(tc.LABEL_INFO, tc.SELENIUM_LOGIN_SUCCESS)
        return driver, session_cookies, viewstate_key

    except Exception as e:
        traceback.print_exc()
        Log.log_message(tc.LABEL_ERROR, f"Selenium login failed: {e}")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return None, None, None


# ============================================================
#   Process Worker
# ============================================================

def process_students_group_worker(args):
    (group_records, current_branch, username, password,
     shared_results, shared_failures, shared_processed_counter,
     shared_departed_counter, task_key) = args

    process_user_data_dir = tempfile.mkdtemp(prefix=f"chrome_{uuid.uuid4()}_")
    process_driver = None
    try:
        process_driver, cookies, viewstate_key = selenium_login_worker(current_branch, process_user_data_dir, username, password)
        if not process_driver:
            Log.log_message(tc.LABEL_ERROR, f"Login failed for branch {current_branch}")
            return

        for student in group_records:
            student_id = student.get(tc.STUDENT_ID_COL_NAME)
            study_type = student.get(tc.STUDY_TYPE_COL_NAME)
            try:
                success = remove_student_by_id_worker(student_id, study_type, process_driver, current_branch, shared_results, shared_failures)
                shared_processed_counter.value += 1
                if success:
                    shared_departed_counter.value += 1
            except Exception as e:
                Log.log_message(tc.LABEL_ERROR, f"Error in worker for {student_id}: {e}")
                add_result(shared_results, student_id, study_type, current_branch, tc.RESULTS_FAILURE, f"Worker error: {str(e)}")
                add_result(shared_failures, student_id, study_type, current_branch, tc.RESULTS_FAILURE, f"Worker error: {str(e)}")
                shared_processed_counter.value += 1

    except Exception as e:
        Log.log_message(tc.LABEL_ERROR, f"Process worker crash: {e}")
        traceback.print_exc()
    finally:
        if process_driver:
            try:
                process_driver.quit()
            except Exception:
                pass
        shutil.rmtree(process_user_data_dir, ignore_errors=True)
        Log.log_message(tc.LABEL_INFO, f"Cleaned up temp dir {process_user_data_dir}")

# noinspection SpellCheckingInspection
class StudentDeparture:
    def __init__(self, talmud):
        self.failure_file_path = None
        self.students_by_branch = None
        self.total_students = None
        self.students_df = talmud.data_df
        self.username = talmud.username
        self.password = talmud.password
        self.departed_counter = 0
        self.processed_counter = 0
        self.current_branch = None
        self.driver = None

        # Results will be collected from shared manager objects
        self.results = ResultsFile()
        self.task_key = getattr(talmud, 'task_key', None)
        self.load_students_data()

    def load_students_data(self, file_path=None):
        if file_path:
            self.students_df = self.students_file_to_df(file_path)
        self.total_students = len(self.students_df)
        self.students_by_branch = self.students_df.groupby(tc.BRANCH_COL_NAME)

    @staticmethod
    def students_file_to_df(file_path):
        """
        Reads a CSV or XLSX file, skips the first two lines, and uses the third line as headers.
        :return: A DataFrame containing the data with proper headers
        """
        # Determine the file type based on the extension
        id_number_dtype = {"StudentIdentity": str}
        # Skip 3 empty rows that exist in the input file.
        skips = 3

        if file_path.lower().endswith('.csv'):
            # Read the CSV file
            df = pd.read_csv(file_path, skiprows=skips, dtype=id_number_dtype)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            # Read the Excel file
            df = pd.read_excel(file_path, skiprows=skips, dtype=id_number_dtype)
        else:
            Log.log_message(tc.LABEL_ERROR, tc.UNSUPPORTED_INPUT_FILE, True)
            raise ValueError(tc.UNSUPPORTED_INPUT_FILE)

        return df

    def set_current_branch(self, branch):
        self.current_branch = None
        try:
            # Convert value to float first to handle all cases (int, float, string of int/float)
            number = float(branch)

            # Convert the float to an integer and format it as a two-digit number
            two_digit_str = f"{int(number):02d}"

            self.current_branch = two_digit_str
        except ValueError:
            pass

    def perform(self):
        result = self._perform()

        # Ensure all processes from first run are completely done before starting rerun
        Log.log_message(tc.LABEL_INFO, "First run completed. Checking for failures before rerun...")

        if not self.failure_file_path:
            # No failures, return immediately
            Log.log_message(tc.LABEL_INFO, "No failures found. Returning results.")
            return result

        # Wait a moment to ensure all process cleanup is complete before starting rerun
        time.sleep(1)
        Log.log_message(tc.LABEL_INFO, f"Starting rerun with failures file: {self.failure_file_path}")

        self.load_students_data(self.failure_file_path)
        self.results.reset()
        self.departed_counter = 0
        self.processed_counter = 0
        
        # Reset progress bar to 0% for rerun
        if self.task_key:
            ProgressManager.set_progress(self.task_key, 0)
        
        rerun_result = self._perform()

        # Ensure all processes from rerun are completely done before returning
        Log.log_message(tc.LABEL_INFO, "Rerun completed. All processes finished.")
        time.sleep(1)

        result[STR_MESSAGE] += f"Rerun has been performed with the following summary: \n{rerun_result[STR_MESSAGE]}"

        # Return the last failure file path (rerun's if exists, otherwise first run's)
        if self.failure_file_path:
            result['file_path'] = self.failure_file_path
        return result

    def _perform(self):
        Log.log_message(tc.LABEL_INFO, tc.DEPARTURE_START, True)

        # Initialize progress to 0%
        if self.task_key:
            ProgressManager.set_progress(self.task_key, 0)

        # Create multiprocessing manager for shared state
        manager = multiprocessing.Manager()
        shared_results = manager.dict({
            tc.STUDENT_ID_COL_NAME: manager.list(),
            tc.STUDY_TYPE_COL_NAME: manager.list(),
            tc.BRANCH_COL_NAME: manager.list(),
            tc.DEPARTED_COL_NAME: manager.list(),
            tc.DETAILS_COL_NAME: manager.list()
        })
        shared_failures = manager.dict({
            tc.STUDENT_ID_COL_NAME: manager.list(),
            tc.STUDY_TYPE_COL_NAME: manager.list(),
            tc.BRANCH_COL_NAME: manager.list(),
            tc.DEPARTED_COL_NAME: manager.list(),
            tc.DETAILS_COL_NAME: manager.list()
        })
        shared_processed_counter = manager.Value('i', 0)  # Shared integer
        shared_departed_counter = manager.Value('i', 0)    # Shared integer

        processes = []

        for branch_num in self.students_by_branch.groups:
            branch_data = self.students_by_branch.get_group(branch_num)
            self.set_current_branch(branch_num)

            if len(branch_data) < tc.THREADS_COUNT * 20:
                students_groups = numpy.array_split(branch_data, 1)
            else:
                students_groups = numpy.array_split(branch_data, tc.THREADS_COUNT)

            if not self.current_branch:
                continue

            Log.log_message(tc.LABEL_INFO, tc.DEPARTURE_BY_BRANCH_START.format(self.current_branch), True)

            # Create one process per student group
            for group in students_groups:
                # Convert DataFrame to list of dicts for pickling (multiprocessing requires picklable objects)
                group_records = group.to_dict('records')

                # Prepare arguments for worker function
                args = (
                    group_records,  # List of dicts instead of DataFrame
                    self.current_branch,
                    self.username,
                    self.password,
                    shared_results,
                    shared_failures,
                    shared_processed_counter,
                    shared_departed_counter,
                    self.task_key
                )

                # Create process
                process = multiprocessing.Process(
                    target=process_students_group_worker,
                    args=(args,)
                )
                process.start()
                processes.append(process)
                Log.log_message(tc.LABEL_INFO, f"Started process {process.pid} for {len(group)} students in branch {self.current_branch}")

            Log.log_message(tc.LABEL_INFO, f"Started {len(students_groups)} process(es) for branch {self.current_branch}")

            # Update progress periodically while processes are running
            if self.task_key:
                while any(p.is_alive() for p in processes[-len(students_groups):]):
                    time.sleep(1)
                    percent = int((shared_processed_counter.value / max(self.total_students, 1)) * 100)
                    ProgressManager.set_progress(self.task_key, min(percent, 100))

        # Wait for ALL processes to complete across all branches
        Log.log_message(tc.LABEL_INFO, f"Waiting for {len(processes)} process(es) to complete...")
        for process in processes:
            process.join()
            if process.exitcode != 0:
                Log.log_message(tc.LABEL_WARNING, f"Process {process.pid} exited with code {process.exitcode}")

        Log.log_message(tc.LABEL_INFO, f"All {len(processes)} process(es) completed")

        # Merge results from shared manager objects into local ResultsFile
        self.processed_counter = shared_processed_counter.value
        self.departed_counter = shared_departed_counter.value

        # Copy shared results to local ResultsFile
        self.results.reset()
        for i in range(len(shared_results[tc.STUDENT_ID_COL_NAME])):
            student_id = shared_results[tc.STUDENT_ID_COL_NAME][i]
            study_type = shared_results[tc.STUDY_TYPE_COL_NAME][i]
            branch = shared_results[tc.BRANCH_COL_NAME][i]
            depart_status = shared_results[tc.DEPARTED_COL_NAME][i]
            depart_details = shared_results[tc.DETAILS_COL_NAME][i]

            self.results.add_result(student_id, study_type, branch, depart_status, depart_details)

        # Final progress update to ensure 100% is reached
        Log.log_message(tc.LABEL_INFO, tc.SUMMARY.format(self.departed_counter, self.total_students, self.processed_counter, self.total_students), True)
        if self.task_key:
            final_percent = int((self.processed_counter / max(self.total_students, 1)) * 100)
            ProgressManager.set_progress(self.task_key, min(final_percent, 100))

        # Verify all processing is complete
        Log.log_message(tc.LABEL_INFO, f"All branches processed. Processed: {self.processed_counter}/{self.total_students} students")

        # Ensure all processes are fully complete before creating the failure file
        time.sleep(1)
        Log.log_message(tc.LABEL_INFO, "All processes completed across all branches. Creating failure file...")

        try:
            self.failure_file_path = self.results.create_file()
            Log.log_message(tc.LABEL_INFO, f"Failure file created: {self.failure_file_path}")
        except Exception as e:
            Log.log_message(tc.LABEL_ERROR, f"Error creating failure file: {e}")
            print(e)

        Log.log_message(tc.LABEL_INFO, tc.DEPARTURE_END, True)
        if self.task_key:
            ProgressManager.finish(self.task_key)
        return {STR_ERROR: False, STR_MESSAGE: tc.S_SUMMARY.format(self.departed_counter, self.total_students, self.processed_counter, self.total_students)}

    def __exit__(self, exc_type, exc_val, exc_tb):
        Log.log_message(tc.LABEL_INFO, f"Exiting {self.__class__.__name__}")
        # סגירת הדפדפן אם נפתח
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        # Note: Each process cleans up its own temp folder, no need to track user_data_dirs here