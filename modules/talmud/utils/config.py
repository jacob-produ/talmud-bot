import configparser
from school_manager.modules.talmud.utils.log import Log
from school_manager.constants.talmud import CONFIG_FILE_PATH, LABEL_INFO

class Config:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)

        self.proxies = {
            "http": config.get('Proxy', 'proxy_server'),
            "https": config.get('Proxy', 'proxy_server')
        }

        self.username = config.get('Creds', 'username')
        self.password = config.get('Creds', 'password')
        self.students_file_path = config.get('General', 'students_file_path')
        self.threads_count = config.getint('General', 'threads_count')
        self.proxy_enabled = config.getboolean('Proxy', "proxy_enabled")
        self.proxy_server = config.get('Proxy', 'proxy_server')

        Log.log_message(LABEL_INFO, {section: dict(config.items(section)) for section in config.sections()})
