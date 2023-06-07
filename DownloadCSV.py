import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def download(folder_name, download_link):
    # Set the login credentials
    username = "jiahaoz3@uic.edu"
    password = "yunyun520"

    # Set the Chrome driver options
    server_dir = os.path.join(os.path.dirname(__file__))
    chrome_options = Options()
    download_dir = os.path.join(server_dir, folder_name)
    chrome_options.add_experimental_option(
        "prefs", {"download.default_directory": download_dir}
    )

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)

    # Log in to the website
    driver.get("https://www.barchart.com/login")
    username_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.CLASS_NAME, "login-button")
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    # Navigate to the download page
    driver.get(download_link)

    time.sleep(5)
    # refresh for the newest data
    refresh_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".toolbar-button.refresh"))
    )
    time.sleep(1)
    refresh_button.click()
    # Find and click the download button
    download_button = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".toolbar-button.download"))
    )
    download_button.click()

    time.sleep(10)
    # Close the web driver
    driver.quit()


# Example usage:
# download("BearCall", "https://www.barchart.com/options/call-spreads/bear-call?orderBy=maxProfitPercent&orderDir=desc")
# download("BullPut", "https://www.barchart.com/options/put-spreads/bull-put?orderBy=maxProfitPercent&orderDir=desc")
# download("IronCon", "https://www.barchart.com/options/short-condors?orderBy=breakEvenProbability&orderDir=desc")
