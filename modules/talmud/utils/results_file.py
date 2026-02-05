import os
import pandas as pd
from datetime import datetime
import school_manager.constants.talmud as tc
from school_manager.modules.talmud.utils.log import Log

class ResultsFile:
    def __init__(self):
        self.failures = None
        self.results = None
        self.reset()

    def reset(self):
        self.results = {tc.STUDENT_ID_COL_NAME: list(),
                        tc.STUDY_TYPE_COL_NAME: list(),
                        tc.BRANCH_COL_NAME: list(),
                        tc.DEPARTED_COL_NAME: list(),
                        tc.DETAILS_COL_NAME: list()}
        self.failures = {tc.STUDENT_ID_COL_NAME: list(),
                        tc.STUDY_TYPE_COL_NAME: list(),
                        tc.BRANCH_COL_NAME: list(),
                        tc.DEPARTED_COL_NAME: list(),
                        tc.DETAILS_COL_NAME: list()}

    def add_result(self, student_id, study_type, branch, depart_status, depart_details):
        self.results[tc.STUDENT_ID_COL_NAME].append(student_id)
        self.results[tc.STUDY_TYPE_COL_NAME].append(study_type)
        self.results[tc.BRANCH_COL_NAME].append(branch)
        self.results[tc.DEPARTED_COL_NAME].append(depart_status)
        self.results[tc.DETAILS_COL_NAME].append(depart_details)

        if depart_status == tc.RESULTS_FAILURE:
            self.failures[tc.STUDENT_ID_COL_NAME].append(student_id)
            self.failures[tc.STUDY_TYPE_COL_NAME].append(study_type)
            self.failures[tc.BRANCH_COL_NAME].append(branch)
            self.failures[tc.DEPARTED_COL_NAME].append(depart_status)
            self.failures[tc.DETAILS_COL_NAME].append(depart_details)

    def create_file(self):
        self.create_results_file()
        return self.create_failures_file()

    def create_results_file(self):
        df = pd.DataFrame(self.results)

        # Create results folder, if exists this line do nothing.
        os.makedirs(tc.RESULTS_FOLDER_NAME, exist_ok=True)

        file_name = tc.RESULTS_FILE_NAME.format(datetime.now().strftime("%d_%m_%y_%H_%M_%S"))

        file_path = os.path.join(tc.RESULTS_FOLDER_NAME, file_name)
        df.to_excel(file_path, index=False)

        Log.log_message(tc.LABEL_INFO, tc.RESULTS_FILE_CREATED)

    def create_failures_file(self):
        if self.failures[tc.STUDENT_ID_COL_NAME]:
            df = pd.DataFrame(self.failures)
            file_name = tc.RESULTS_FAILURES_FILE_NAME.format(datetime.now().strftime("%d_%m_%y_%H_%M_%S"))
            file_path = os.path.join(tc.RESULTS_FOLDER_NAME, file_name)
            df.to_excel(file_path, startrow=3, index=False)
            Log.log_message(tc.LABEL_INFO, tc.RESULTS_FAILURES_FILE_CREATED)
            return file_path

        return None
