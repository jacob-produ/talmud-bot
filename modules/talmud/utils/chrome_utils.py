import os
import shutil
from selenium import webdriver
from core.messages import LABEL_INFO
from selenium.webdriver.common.by import By
import school_manager.constants.talmud as tc
from selenium.webdriver.chrome.options import Options
from school_manager.modules.talmud.utils.log import Log
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
import school_manager.constants.talmud as talmud_constants
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common import TimeoutException, ElementClickInterceptedException


def clear_temp_files():
    try:
        for d in os.listdir("/tmp"):
            if d.startswith("chrome_"):
                shutil.rmtree(os.path.join("/tmp", d), ignore_errors=True)
    except Exception:
        pass

def perform_login(driver, username, password):
    """
    Login to Talmud system using the same method as send_reports.py
    This bypasses 2FA by going directly to default.aspx after login
    """
    import time
    
    try:
        # Step 1: Go to login page
        driver.get("https://talmud.edu.gov.il/Login.aspx?ReturnUrl=%2f")
        time.sleep(3)
        
        # Step 2: Enter credentials
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.ID, "txtUserName"))
        ).send_keys(username)
        driver.find_element(By.ID, "txtPassword").send_keys(password)
        driver.find_element(By.ID, "LoginButton").click()
        time.sleep(4)
        
        # Step 3: Skip 2FA popup by clicking Cancel
        try:
            driver.find_element(By.ID, "ucMessagePopUp_btnMCancel").click()
            time.sleep(2)
        except:
            pass
        
        # Step 4: Navigate directly to default.aspx (bypasses 2FA)
        driver.get("https://talmud.edu.gov.il/default.aspx")
        time.sleep(3)
        
        # Step 5: Verify login by checking for menu
        try:
            driver.find_element(By.ID, "ucUpperMenu_dlUpderMenu_lnkUperMenu_0")
            Log.log_message(LABEL_INFO, "Login successful!")
            
            # Step 6: Click on עמותות menu to access branches
            driver.find_element(By.ID, "ucUpperMenu_dlUpderMenu_lnkUperMenu_0").click()
            time.sleep(3)
            Log.log_message(LABEL_INFO, "Navigated to associations menu")
            
            return True
        except:
            Log.log_message(tc.LABEL_ERROR, "Login failed - menu not found")
            return False
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        Log.log_message(tc.LABEL_ERROR, tc.SELENIUM_LOGIN_FAIL)
        Log.log_message(tc.LABEL_ERROR, e)
        Log.log_message(tc.LABEL_ERROR, traceback.format_exc())
        return False

def _login(driver, username, password):
    import time
    
    # Wait until the username input is available and fill it
    username_input = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "txtUserName")))
    username_input.clear()
    username_input.send_keys(username)
    time.sleep(1)

    # Fill in the password field
    password_input = driver.find_element(By.ID, "txtPassword")
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(1)

    # Click the login button
    driver.find_element(By.ID, "LoginButton").click()
    time.sleep(4)

    # Try to close any popup (2FA or warning)
    try:
        cancel_btn = driver.find_element(By.ID, "ucMessagePopUp_btnMCancel")
        cancel_btn.click()
        time.sleep(2)
    except:
        pass

    close_warning_popup(driver)

    # Navigate directly to default.aspx to bypass 2FA
    # This is the same technique used by Bot3 in תלמוד דוחות
    driver.get("https://talmud.edu.gov.il/default.aspx")
    time.sleep(3)
    
    # Verify login by checking if we can find the reports menu
    try:
        WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "ucUpperMenu_dlUpderMenu_lnkUperMenu_2")))
        Log.log_message(LABEL_INFO, "Login successful - found reports menu")
    except TimeoutException:
        # If reports menu not found, check URL
        if "default.aspx" in driver.current_url.lower():
            Log.log_message(LABEL_INFO, "Login successful - on default page")
        else:
            raise Exception("Login failed - could not verify login success")


def close_login_popup(driver):
    try:
        popup_close = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, "LoginFirstPopUpMessage1_btnCloseMessege")))
        Log.log_message(LABEL_INFO, f"Welcome message found, closing...")
        popup_close.click()
    except TimeoutException:
        Log.log_message(LABEL_INFO, f"No Welcome message..")
    except Exception as e:
        Log.log_message(LABEL_INFO, f"Failed to close welcome message {e}")
    return

def close_warning_popup(driver):
    try:
        popup_close = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.ID, "ucMessagePopUp_spanBtnOk")))
        Log.log_message(LABEL_INFO, f"Warning message found, closing...")
        popup_close.click()
    except TimeoutException:
        Log.log_message(LABEL_INFO, f"No Warning message..")
    except Exception as e:
        Log.log_message(LABEL_INFO, f"Failed to close warning message {e}")


def get_chrome_driver(user_data_dir):
    clear_temp_files()

    chrome_options = Options()

    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    for argument in tc.CHROME_ARGUMENTS:
        chrome_options.add_argument(argument)
    for experimental in tc.CHROME_EXPERIMENTAL:
        chrome_options.add_experimental_option(*experimental)

    chrome_options.add_experimental_option("prefs", tc.PREFS)

    chrome_driver_service = ChromeService(ChromeDriverManager().install())

    # Set up the Burp Suite proxy
    if talmud_constants.PROXY_ENABLED:
        proxy = talmud_constants.PROXY_SERVER.replace("http://","")  # Replace http with your Burp Suite proxy address and port
        chrome_options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=chrome_options, service=chrome_driver_service)
    return driver