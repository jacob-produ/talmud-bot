import uuid
import shutil
import tempfile
from time import sleep
from datetime import datetime
from core.messages import LABEL_INFO
from selenium.webdriver.common.by import By
import school_manager.constants.talmud as tc
from school_manager.modules.talmud.utils.log import Log
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as ec
import school_manager.modules.talmud.utils.chrome_utils as c_utils
from selenium.common import TimeoutException, NoSuchElementException
from school_manager.modules.talmud.utils.progress import ProgressManager
from school_manager.constants.constants import STR_ERROR, STR_MESSAGE, STR_FILE_DATA


# noinspection DuplicatedCode
class AddStudents:

    def __init__(self, talmud):
        self.talmud = talmud
        self.branch = talmud.branch
        self.username = talmud.username
        self.password = talmud.password
        self.driver = None
        self.user_data_dir = tempfile.mkdtemp(prefix=f"chrome_{uuid.uuid4()}_")
        self.task_key = getattr(talmud, 'task_key', None)
        self.manual = talmud.data_df["inputMethod"] == "manual"
        self.skip_existing_students = talmud.data_df["skipExistingStudents"] == "on"
        self.student_data = talmud.data_df if self.manual else None
        self.students_df =  talmud.data_df["data_df"] if not self.manual else None
        Log.log_message(LABEL_INFO, f"Skipped existing students: {self.skip_existing_students}")

    def perform(self):
        try:
            Log.log_message(tc.LABEL_INFO, tc.ADD_START)
            if self.manual:
                result = self.add_from_manual(self.student_data)
            else:
                result = self.add_from_file_by_manual()
            Log.log_message(tc.LABEL_INFO, tc.ADD_END)

            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {STR_ERROR: True, STR_MESSAGE: str(e)}

    def add_from_manual(self, student_data):
        self.driver = c_utils.get_chrome_driver(self.user_data_dir)
        success = c_utils.perform_login(self.driver, self.username, self.password)

        if success:
            try:
                study_type = self.student_data["studyType"]
                result1 = self.navigate_to_add_student(study_type)
                if result1:
                    return result1
                date_split = student_data["birthDate"].split('-')
                formatted_entry_date = f"{date_split[2]}-{date_split[1]}-{date_split[0]}"
                student_data["birthDate"] = formatted_entry_date
                return self.add_single_student(student_data, study_type)
            except Exception as e:
                import traceback
                traceback.print_exc()
                Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
                Log.log_message(tc.LABEL_ERROR, e)
        return {STR_ERROR: True, STR_MESSAGE: "משהו השתבש, נסה שוב"}

    def add_single_student(self, student_data, study_type):
        result2 = self.fill_initial_data(student_data, study_type)

        if result2:
            return result2

        return self.fill_full_data(student_data)

    def navigate_to_add_student(self, study_type):
        # Wait until the element with the specific class and title is present and clickable
        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.XPATH, f"//a[contains(@class, 'ucTalmudSideBar_tvTalmud') and @title='{self.branch}']")))

        # Find the branch expand button.
        links = self.driver.find_element(By.ID, "ucTalmudSideBar_tvTalmudn0Nodes").find_elements(By.TAG_NAME, "a")

        branch_found = False
        for link in links:
            if f"Expand {self.branch}" == link.accessible_name:
                link.click()
                branch_found = True
                break

        if not branch_found:
            return {STR_ERROR: True, STR_MESSAGE: tc.ADD_BRANCH_NOT_FOUND.format(self.branch)}

        sleep(1)
        # Find the study type link.
        links = self.driver.find_element(By.ID, "ucTalmudSideBar_tvTalmudn0Nodes").find_elements(By.TAG_NAME, "a")
        study_type_found = False

        for link in links:
            if study_type in link.accessible_name:
                link.click()
                study_type_found = True
                break

        if not study_type_found:
            return {STR_ERROR: True, STR_MESSAGE: tc.ADD_STUDY_NOT_FOUND.format(study_type, self.branch)}
        sleep(1)

        # Find the student list button.
        mosad_students_tab = WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.ID, "__tab_ContentPlaceHolder1_tabStudyTypeDetails_StudentList"))
        )
        mosad_students_tab.click()

        return None

    def fill_initial_data(self, student_data, study_type):
        # Find the add student button.
        add_student_button = WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_divButtonNew")))
        add_student_button.click()

        sleep(1)
        WebDriverWait(self.driver, 10).until(ec.presence_of_element_located((By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_ddlPopIdentityType")))

        select_id_type = Select(self.driver.find_element(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_ddlPopIdentityType"))
        select_id_type.select_by_value(student_data["idType"])

        # If the id type is passport (2) we need to insert origin and birthdate.
        if student_data["idType"] == '2':
            select_id_type = Select(self.driver.find_element(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_ddlCountryOfOrigine"))
            select_id_type.select_by_value(student_data["origin"])

            b_date = student_data["birthDate"]
            self.driver.execute_script(f"document.getElementById('ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_ctlBirthDate_txtDate').value = '{b_date}';")

        id_input_element = self.driver.find_element(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_txtIdentifier")
        id_input_element.send_keys(student_data["idNumber"])

        # click upload
        ok_button = WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_LinkButton1")))
        ok_button.click()

        sleep(1)

        # Check for errors with data inserted.
        if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_PopupBody"):
            errors = ""

            # Check for passport origin error
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valStudentIdentifier"):
                errors += "[סוג מזהה תלמיד הינו חובה]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valCountryOfOrigine"):
                errors += "[ארץ דרכון הינו חובה]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valID"):
                errors += "[ת.ז/דרכון הינו חובה]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_cvalID"):
                errors += "[מספר זהות לא חוקי]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_cvalPassport"):
                errors += "[מספר דרכון צריך להכיל יותר מארבע תווים]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valPassportCheckIsValid"):
                errors += "[מספר דרכון לא תקין, יש להכניס אותיות אנגליות גדולות ומספרים בלבד]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_cvalIdentityCardCheck"):
                errors += "[אורך מספר תעודת זהות אינו תקין]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valMexicanPassport"):
                errors += "[יש לקלוט מספר דרכון מקסיקני בן 16 תווים בלבד, ללא הספרות הראשונות]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valLongPassport"):
                errors += "[מספר דרכון לא יכול להיות ארוך מ-16 תווים]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_ctlBirthDate_valcustdate"):
                errors += "[תאריך לידה לא תקין]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_validDate"):
                errors += "[תאריך לידה הינו חובה]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valBirthDate"):
                errors += "[תאריך לידה לא חוקי במערכת]"
            if self.element_visible(By.ID, "ContentPlaceHolder1_tabStudyTypeDetails_StudentList_ucStudentsSearchDetails_valBirthDateGreater"):
                errors += "[ניתן להזין תאריך לידה החל משנת 1906]"

            if errors:
                return {STR_ERROR: True, STR_MESSAGE: errors}

        # Check if an error alert has been shown.
        try:
            alert_window = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located((By.ID, "ucMessagePopUp_divMessageBox")))
            sleep(1)
            message_label = self.driver.find_element(By.ID, "ucMessagePopUp_lblMessage")
            if "תלמיד זה רשום כבר במוסד זה." in message_label.text:
                if self.skip_existing_students:
                    cancel_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMCancel")))
                    cancel_button.click()
                    Log.log_message(tc.LABEL_ERROR, tc.STUDENT_TRANSFER_NEEDED.format(student_data['idNumber'], self.branch))
                    return {STR_ERROR: True, STR_MESSAGE: tc.STUDENT_TRANSFER_NEEDED.format(student_data['idNumber'], self.branch)}
                else:
                    continue_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_spanBtnOk")))
                    continue_button.click()
                    continue_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMOK")))
                    continue_button.click()
                    return {STR_ERROR: False, STR_MESSAGE: tc.STUDENT_TRANSFER_SUCCESS}
            if "התלמיד כבר קיים במוסד ובסוג לימוד הבאים!" in message_label.text:
                ok_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMCancel")))
                ok_button.click()
                Log.log_message(tc.LABEL_ERROR, tc.STUDENT_ALREADY_REGISTERED.format(student_data['idNumber'], self.branch, study_type))
                return {STR_ERROR: True, STR_MESSAGE: tc.STUDENT_ALREADY_REGISTERED.format(student_data['idNumber'], self.branch, study_type)}
            if "תלמיד זה רשום כבר במוסד אחר" in message_label.text:
                if self.skip_existing_students:
                    cancel_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMCancel")))
                    cancel_button.click()
                    Log.log_message(tc.LABEL_ERROR, tc.STUDENT_TRANSFER_NEEDED.format(student_data['idNumber'], self.branch))
                    return {STR_ERROR: True, STR_MESSAGE: tc.STUDENT_TRANSFER_NEEDED.format(student_data['idNumber'], self.branch)}
                else:
                    continue_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_spanBtnOk")))
                    continue_button.click()
                    continue_button = WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMOK")))
                    continue_button.click()
                    return {STR_ERROR: False, STR_MESSAGE: tc.STUDENT_TRANSFER_SUCCESS}
        except TimeoutException:
            pass

        return {STR_ERROR: False, STR_MESSAGE: tc.STUDENT_ADDED_SUCCESS}

    def element_exists(self, by, value):
        try:
            self.driver.find_element(by, value)
            return True
        except NoSuchElementException:
            return False

    def element_visible(self, by, value):
        try:
            WebDriverWait(self.driver, 0.1).until(ec.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def fill_full_data(self, student_data):
        try:
            sleep(1)
            WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((By.ID, "ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_ctlBirthDate_txtDate")))

            b_date = student_data["birthDate"]
            self.driver.execute_script(f"document.getElementById('ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_ctlBirthDate_txtDate').value = '{b_date}';")

            txt_first_name = self.driver.find_element(By.ID, "ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_txtFirstName")
            txt_first_name.send_keys(student_data["firstName"])

            txt_last_name = self.driver.find_element(By.ID, "ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_txtLastName")
            txt_last_name.send_keys(student_data["lastName"])

            sleep(1)
            select_gender = Select(self.driver.find_element(By.ID, "ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_ddlGender"))
            select_gender.select_by_value(student_data["gender"])

            sleep(1)
            select_marital_status = Select(self.driver.find_element(By.ID, "ContentPlaceHolder1_TabsStudent_StudentDetails1_ucStudentDetails_ddlFamilyStatus"))
            select_marital_status.select_by_value(student_data["maritalStatus"])

            sleep(1)

            save_button = WebDriverWait(self.driver, 2).until(ec.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnSave")))
            save_button.click()

            continue_button = WebDriverWait(self.driver, 2).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_btnMOK")))
            continue_button.click()

            success_window = WebDriverWait(self.driver, 4).until(ec.presence_of_element_located((By.ID, "ucMessagePopUp_lblMessage")))

            if success_window.text == 'שמירת תלמיד בוצעה בהצלחה':
                return {STR_ERROR: False, STR_MESSAGE: 'שמירת תלמיד בוצעה בהצלחה'}
            return {STR_ERROR: False, STR_MESSAGE: success_window.text}
        except TimeoutException:
            return {STR_ERROR: True, STR_MESSAGE: "משהו השתבש, נסה שוב"}

    def add_from_file_by_manual(self):
        results = list()
        total_count = 0
        fails_count = 0
        students_by_study = self.students_df.groupby("סוג לימודים")
        try:
            self.driver = c_utils.get_chrome_driver(self.user_data_dir)
            success = c_utils.perform_login(self.driver, self.username, self.password)

            if success:
                for study_type, students in students_by_study:
                    self.navigate_to_add_student(study_type=str(study_type))
                    # study_type_students = students_by_study[study_type]

                    for index, student in students.iterrows():
                        total_count += 1
                        student_data = dict()
                        student_data["idType"] = str(student["סוג מזהה"])
                        student_data["idNumber"] = str(student["ת.ז./ דרכון"])
                        student_data["firstName"] = str(student["פרטי"])
                        student_data["lastName"] = str(student["משפחה"])
                        student_data["gender"] = str(student["מגדר"])
                        student_data["maritalStatus"] = str(student["מצב משפחתי"])
                        student_data["birthDate"] = datetime.strptime(str(student["ת. לידה"]), '%d/%m/%Y').strftime('%d-%m-%Y')
                        student_data["origin"] = str(student["מוצא"])
                        # self.fill_initial_data(self.driver, student_data, study_type)
                        # self.fill_full_data(self.driver, student_data)

                        result = self.add_single_student(student_data, study_type)

                        if result:
                            results.append([student_data["idNumber"], int(not result["error"]), result["message"]])

                            if result["error"]:
                                fails_count += 1

                        if self.task_key:
                            percent = int((total_count / max(len(self.students_df), 1)) * 100)
                            ProgressManager.set_progress(self.task_key, percent)
                return {STR_ERROR: False, STR_MESSAGE: tc.ADD_SUCCESS.format(fails_count, total_count), STR_FILE_DATA: results}
            return {STR_ERROR: True, STR_MESSAGE: "משהו השתבש אנא נסה שוב"}

        except Exception as e:
            import traceback
            traceback.print_exc()
            Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
            Log.log_message(tc.LABEL_ERROR, e)
            return {STR_ERROR: True, STR_MESSAGE: str(e)}

    def add_from_file_by_batch(self):
        self.driver = c_utils.get_chrome_driver(self.user_data_dir)
        success = c_utils.perform_login(self.driver, self.username, self.password)
        if success:
            try:
                # Get cookies from the driver
                cookies = self.driver.get_cookies()
                session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

                # Wait until the element with the specific class and title is present and clickable
                branch_tab = WebDriverWait(self.driver, 20).until(
                    ec.element_to_be_clickable(
                        (By.XPATH, f"//a[contains(@class, 'ucTalmudSideBar_tvTalmud') and @title='{self.branch}']")
                    )
                )
                # Click on the element
                branch_tab.click()

                mosad_students_tab = WebDriverWait(self.driver, 20).until(
                    ec.element_to_be_clickable((By.ID, "__tab_ContentPlaceHolder1_tabInstituteDetails_TabPanel1"))
                )
                mosad_students_tab.click()

                upload_students = WebDriverWait(self.driver, 20).until(
                    ec.element_to_be_clickable(
                        (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_btnGetExcel"))
                )
                upload_students.click()

                WebDriverWait(self.driver, 20).until(ec.presence_of_element_located((By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_Div3")))

                file_input = self.driver.find_element(By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_flUpload")
                file_input.send_keys(tc.UPLOAD_ADD_FILE_PATH)

                # click upload
                ok_button = WebDriverWait(self.driver, 20).until(
                    ec.element_to_be_clickable(
                        (By.ID, "ContentPlaceHolder1_tabInstituteDetails_TabPanel1_ucStudentsSearch_btnUploadFile"))
                )
                ok_button.click()

                return {STR_ERROR: False, STR_MESSAGE: tc.ADD_STUDENT_SUCCESS}

            except Exception as e:
                import traceback
                traceback.print_exc()
                Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
                Log.log_message(tc.LABEL_ERROR, e)
                return {STR_ERROR: True, STR_MESSAGE: str(e)}
        return {STR_ERROR: True, STR_MESSAGE: "משהו השתבש, אנא נסה שוב"}

    def __exit__(self, exc_type, exc_val, exc_tb):
        Log.log_message(tc.LABEL_INFO, f"Exiting {self.__class__.__name__}")
        # סגירת הדפדפן אם נפתח
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        # מחיקת התיקייה
        if self.user_data_dir:
            Log.log_message(tc.LABEL_INFO, f"Delete folder {self.user_data_dir}")
            shutil.rmtree(self.user_data_dir, ignore_errors=True)