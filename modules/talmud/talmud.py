import school_manager.constants.talmud as tc
from school_manager.modules.talmud.actions import *
from school_manager.constants.constants import STR_MESSAGE, STR_ERROR
from school_manager.modules.talmud.utils.extract_students_info import ExtractStudentsInfo
class Talmud:

    def __init__(self,data, username, password, branch=None, task_key=None):
        self.data_df = data
        self.username = username
        self.password = password
        self.branch = branch
        self.task_key = task_key

    def perform(self, task_type):
        if task_type == tc.TASK_REMOVE_STUDENTS:
            return StudentDeparture(self).perform()
        elif task_type == tc.TASK_APPROVE_STUDENTS:
            return ApproveStudents(self).perform()
        elif task_type == tc.TASK_REJECT_STUDENTS:
            return ApproveStudents(self, approve=False).perform()
        elif task_type == tc.TASK_ADD_STUDENTS:
            return AddStudents(self).perform()
        elif task_type == "extract":
            return ExtractStudentsInfo(self).perform()
        else:
            return {STR_ERROR: True, STR_MESSAGE: tc.NO_ACTION_FOUND}


if __name__ == '__main__':
    Talmud(None, "tl37626700","Liron321", "00").perform("extract")