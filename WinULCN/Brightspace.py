from credentials import Username, Password, Secret_Key
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://brightspace.universiteitleiden.nl"
driver = webdriver.Chrome()

driver.get(url)

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    current_url = driver.current_url

    if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
        print("FAILED")

        username_input = driver.find_element(By.NAME, "Ecom_User_ID")
        password_input = driver.find_element(By.NAME, "Ecom_Password")

        username_input.send_keys(Username)
        password_input.send_keys(Password)

        login_button = driver.find_element(By.ID, "loginbtn")
        login_button.click()

        time.sleep(0.5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        redirected_url = driver.current_url
        print(redirected_url)
        if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):

            next_button = driver.find_element(By.ID, "loginButton2")
            next_button.click()

        else:
            print("Password incorrect")
        
        input("Press")

    elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
        print("SUCCESS")
    else:
        print("UNKNOWN URL")

finally:
    print("Done with the script")
    driver.quit()
