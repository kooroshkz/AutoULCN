import os
import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import appdirs
from configparser import ConfigParser
from time import sleep

app_name = "AUTOULCN"
config_dir = appdirs.user_data_dir(app_name)
config_path = os.path.join(config_dir, 'config.ini')

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Fetch or write credentials from a config file
def get_credentials():
    config = ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
        username = config.get('Credentials', 'username', fallback=None)
        password = config.get('Credentials', 'password', fallback=None)
        secret_key = config.get('Credentials', 'secret_key', fallback=None)
    else:
        username = password = secret_key = None

    if not username:
        username = input("Enter Username: ")
    if not password:
        password = input("Enter Password: ")
    if not secret_key:
        secret_key = input("Enter Secret Key: ")

    # Save the credentials back to the config file
    config['Credentials'] = {
        'username': username,
        'password': password,
        'secret_key': secret_key
    }
    with open(config_path, 'w') as configfile:
        config.write(configfile)

    return username, password, secret_key

Username, Password, Secret_Key = get_credentials()

# Selenium automation script
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
        sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
        break

driver.quit()
