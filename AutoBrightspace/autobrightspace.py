import os
import platform
import subprocess
import sys
import pyotp
import appdirs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser
from time import sleep

# List of dependencies to check and install
required_modules = ['pyotp', 'selenium', 'appdirs', 'pyinstaller']

app_name = "AutoBrightspace"
config_dir = appdirs.user_data_dir(app_name)
config_path = os.path.join(config_dir, 'config.ini')

# Path to the icon (assumed to be in the "icon" folder)
icon_path_windows = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.ico')
icon_path_mac = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.icns')

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Function to check and install missing dependencies
def install_dependencies():
    print("Checking and installing dependencies...")
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"Module '{module}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    print("All dependencies are installed.")

# Get credentials from the config file
def get_credentials(prompt_for_update=False):
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

    elif prompt_for_update:
        print(f"Current Username: {username}")
        new_username = input("Enter new Username (or press Enter to keep the current one): ")
        if new_username:
            username = new_username

    if not password:
        password = input("Enter Password: ")

    elif prompt_for_update:
        masked_password = password[0] + "*" * (len(password) - 2) + password[-1]
        print(f"Current Password: {masked_password}")
        new_password = input("Enter new Password (or press Enter to keep the current one): ")
        if new_password:
            password = new_password

    if not secret_key:
        secret_key = input("Enter Secret Key: ")

    elif prompt_for_update:
        print(f"Current Secret Key: {secret_key}")
        new_secret_key = input("Enter new Secret Key (or press Enter to keep the current one): ")
        if new_secret_key:
            secret_key = new_secret_key

    if prompt_for_update:
        config['Credentials'] = {
            'username': username,
            'password': password,
            'secret_key': secret_key
        }

        with open(config_path, 'w') as configfile:
            config.write(configfile)

    return username, password, secret_key

# Build executable with custom icon
def build_executable():
    current_os = platform.system().lower()
    try:
        if current_os == "windows" and os.path.exists(icon_path_windows):
            subprocess.run(["pyinstaller", "--onefile", "--icon", icon_path_windows, "autobrightspace.py", "--name", "AutoBrightspace.exe"])
        elif current_os == "darwin" and os.path.exists(icon_path_mac):  # macOS
            subprocess.run(["pyinstaller", "--onefile", "--icon", icon_path_mac, "autobrightspace.py", "--name", "AutoBrightspace.dmg"])
        elif current_os == "linux":
            subprocess.run(["pyinstaller", "--onefile", "autobrightspace.py", "--name", "AutoBrightspace"])
        else:
            print(f"Unsupported OS or icon not found: {current_os}.")
            return False
        print(f"Executable built successfully.")
    except FileNotFoundError:
        print("PyInstaller not found. Please ensure it is installed.")
        return False

def run_program():
    username, password, secret_key = get_credentials(prompt_for_update=False)

    driver = webdriver.Chrome()
    driver.get("https://brightspace.universiteitleiden.nl")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    current_url = driver.current_url
    if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
        username_input = driver.find_element(By.NAME, "Ecom_User_ID")
        password_input = driver.find_element(By.NAME, "Ecom_Password")

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_button = driver.find_element(By.ID, "loginbtn")
        login_button.click()

        WebDriverWait(driver, 10).until(url_changes(current_url))
        redirected_url = driver.current_url

        if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
            next_button = driver.find_element(By.ID, "loginButton2")
            next_button.click()

            totp = pyotp.TOTP(secret_key)
            totp_code = totp.now()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))
            code_input = driver.find_element(By.ID, "nffc")
            code_input.send_keys(totp_code)

            next_button_after_code = driver.find_element(By.ID, "loginButton2")
            next_button_after_code.click()
        else:
            print("Login failed or incorrect credentials.")
    elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
        print("Already logged in.")
    else:
        print("Unknown URL detected.")

    try:
        while driver.current_window_handle:  # Loop until browser window is open
            sleep(1)
    except Exception:
        print("Browser window closed unexpectedly. Exiting program.")
    finally:
        try:
            driver.quit()
        except Exception:
            print("Browser already closed.")
        print("Browser closed, script terminated.")

def url_changes(old_url):
    def _url_changes(driver):
        return driver.current_url != old_url
    return _url_changes

if __name__ == "__main__":
    # Automatically run the program without needing to pass --run when built as an executable
    if len(sys.argv) == 1:
        run_program()
    elif "--setup" in sys.argv:
        install_dependencies()
    elif "--configue" in sys.argv:
        get_credentials(prompt_for_update=True)
    elif "--build" in sys.argv:
        build_executable()
    elif "--help" in sys.argv:
        print("Available commands:\n"
              "--setup     Install all dependencies.\n"
              "--configue  Configure username, password, and secret key.\n"
              "--build     Build an executable based on your OS.\n"
              "--help      Display this help message.")
    else:
        print("Use --help for available commands.")
