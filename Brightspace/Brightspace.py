import os
import time, pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

script_dir = os.path.dirname(__file__)
credentials_file_path = os.path.join(script_dir, 'Credentials.txt')

# You can hardcode your credentials here.
# Username = "Your Username"
# Password = "Your Password"
# Secret_Key = "Your Secret Key"

# And comment out the following code block.
with open(credentials_file_path, 'r') as file:

    for line in file:
        variable, value = line.strip().split(' = ')
        value = value.strip('"')
        exec(f'{variable} = "{value}"')


url = "https://brightspace.universiteitleiden.nl"
driver = webdriver.Chrome()

driver.get(url)

def url_changes(old_url):
    def _url_changes(driver):
        return driver.current_url != old_url
    return _url_changes


WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

current_url = driver.current_url

if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
    print("Login required!")

    username_input = driver.find_element(By.NAME, "Ecom_User_ID")
    password_input = driver.find_element(By.NAME, "Ecom_Password")

    username_input.send_keys(Username)
    password_input.send_keys(Password)

    login_button = driver.find_element(By.ID, "loginbtn")
    login_button.click()

    WebDriverWait(driver, 10).until(url_changes(current_url))

    redirected_url = driver.current_url
    print(redirected_url)

    if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
        next_button = driver.find_element(By.ID, "loginButton2")
        next_button.click()

        totp = pyotp.TOTP(Secret_Key)
        totp_code = totp.now()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))

        code_input = driver.find_element(By.ID, "nffc")
        code_input.send_keys(totp_code)
        next_button_after_code = driver.find_element(By.ID, "loginButton2")
        next_button_after_code.click()
    else:
        print("Password incorrect")

elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
    print("Already Signed In")
else:
        print("UNKNOWN URL")

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
        break

driver.quit()
