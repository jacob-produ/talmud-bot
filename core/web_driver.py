import os
from selenium import webdriver
from core import download_utils
from social_security_robot import config


def create_driver():
    prefs = {"plugins.always_open_pdf_externally": True,
             "download.default_directory": download_utils.DOWNLOAD_DIR,
             "profile.default_content_setting_values.automatic_downloads": 1,
             "profile.default_content_settings.popups": 0,
             }
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])

    # Set headless mode in ubuntu server
    if os.name != 'nt' or config.HEADLESS:
        options.add_argument("--headless")
        options.add_argument('window-size=1680x1050')
        options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    download_utils.allow_download_files_from_server(driver)

    driver.implicitly_wait(10)

    # Setting up Chrome/83.0.4103.53 as useragent
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})

    return driver
