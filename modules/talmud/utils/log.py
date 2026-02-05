from datetime import datetime
from school_manager.constants.talmud import LOG_FILE_PATH

class Log:
    @staticmethod
    def log_message(label, message, to_console=False):
        with open(LOG_FILE_PATH, "a",  errors="replace") as log_file:
            log_file.write(datetime.now().isoformat() + " {} {}".format(label, message) + "\n")
            if to_console:
                print(message)