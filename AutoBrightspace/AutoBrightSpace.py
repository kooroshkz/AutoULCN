import os
import platform
import subprocess
import sys
import threading
import datetime
import appdirs
import pyotp
import argparse
from configparser import ConfigParser
from time import sleep

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QLineEdit, QTabWidget, QFrame, QTextEdit, 
                           QProgressBar, QComboBox, QMessageBox, QGridLayout, QSplitter,
                           QStackedWidget, QFileDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# App constants
APP_NAME = "AutoBrightspace"
CONFIG_DIR = appdirs.user_data_dir(APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.ini')

# Path to the icon (assumed to be in the "icon" folder)
ICON_PATH_WINDOWS = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.ico')
ICON_PATH_MAC = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.icns')
ICON_PATH_LINUX = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.png')

# List of dependencies to check and install
REQUIRED_MODULES = ['pyotp', 'selenium', 'appdirs', 'pyinstaller', 'webdriver-manager', 'pillow', 'PyQt5']

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

class LoginWorker(QThread):
    """Worker thread for handling login process"""
    status_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(float)
    log_message = pyqtSignal(str)
    process_finished = pyqtSignal()
    
    def __init__(self, username, password, secret_key):
        super().__init__()
        self.username = username
        self.password = password
        self.secret_key = secret_key
        self.driver = None
        self.is_running = True
        
    def run(self):
        try:
            self.status_update.emit("Initializing browser...", "yellow")
            self.log_message.emit("Starting automated login process")
            
            # Initialize Chrome driver
            self.progress_update.emit(0.3)
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            
            self.status_update.emit("Navigating to login page...", "yellow")
            self.log_message.emit("Opening Brightspace login page")
            self.driver.get("https://brightspace.universiteitleiden.nl")
            
            self.progress_update.emit(0.4)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            current_url = self.driver.current_url
            
            # Handle SURFconext university selection page
            if current_url.startswith("https://engine.surfconext.nl/authentication/idp"):
                self.status_update.emit("Selecting Leiden University...", "yellow")
                self.log_message.emit("Detected SURFconext page, selecting Leiden University")
                
                try:
                    # Wait for and click the Leiden University option
                    leiden_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//div[@data-entityid='https://login.uaccess.leidenuniv.nl/nidp/saml2/metadata']"))
                    )
                    leiden_button.click()
                    self.log_message.emit("Clicked on Leiden University option")
                    
                    # Wait for page to change after clicking
                    WebDriverWait(self.driver, 10).until(self.url_changes(current_url))
                    current_url = self.driver.current_url
                    self.log_message.emit(f"Redirected to: {current_url}")
                    
                except Exception as e:
                    self.log_message.emit(f"Failed to select Leiden University: {str(e)}")
                    # Try alternative method - click the submit button inside the form
                    try:
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, 
                                "//form[@action='https://engine.surfconext.nl/authentication/idp/process-wayf']//button[@type='submit']"))
                        )
                        submit_button.click()
                        self.log_message.emit("Clicked submit button as fallback")
                        WebDriverWait(self.driver, 10).until(self.url_changes(current_url))
                        current_url = self.driver.current_url
                    except Exception as e2:
                        self.log_message.emit(f"Fallback method also failed: {str(e2)}")
            
            if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
                self.status_update.emit("Entering credentials...", "yellow")
                self.log_message.emit("Entering username and password")
                
                username_input = self.driver.find_element(By.NAME, "Ecom_User_ID")
                password_input = self.driver.find_element(By.NAME, "Ecom_Password")
                
                username_input.send_keys(self.username)
                password_input.send_keys(self.password)
                
                self.progress_update.emit(0.5)
                login_button = self.driver.find_element(By.ID, "loginbtn")
                login_button.click()
                
                WebDriverWait(self.driver, 10).until(self.url_changes(current_url))
                redirected_url = self.driver.current_url
                
                if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
                    self.status_update.emit("Handling 2FA...", "yellow")
                    self.log_message.emit("Processing two-factor authentication")
                    
                    self.progress_update.emit(0.7)
                    next_button = self.driver.find_element(By.ID, "loginButton2")
                    next_button.click()
                    
                    totp = pyotp.TOTP(self.secret_key)
                    totp_code = totp.now()
                    
                    self.log_message.emit(f"Generated TOTP code: {totp_code}")
                    
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))
                    code_input = self.driver.find_element(By.ID, "nffc")
                    code_input.send_keys(totp_code)
                    
                    self.progress_update.emit(0.9)
                    next_button_after_code = self.driver.find_element(By.ID, "loginButton2")
                    next_button_after_code.click()
                    
                    self.progress_update.emit(1.0)
                    self.status_update.emit("Login successful! Browser ready", "green")
                    self.log_message.emit("✓ Login completed successfully")
                else:
                    self.status_update.emit("Login failed - check credentials", "red")
                    self.log_message.emit("✗ Login failed or incorrect credentials")
                    
            elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
                self.progress_update.emit(1.0)
                self.status_update.emit("Already logged in!", "green")
                self.log_message.emit("✓ Already logged in to Brightspace")
            else:
                self.status_update.emit("Unknown page detected", "orange")
                self.log_message.emit(f"? Unknown URL detected: {current_url}")
            
            # Monitor browser until closed
            self.monitor_browser()
            
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}", "red")
            self.log_message.emit(f"✗ Error during login: {str(e)}")
            self.process_finished.emit()
    
    def monitor_browser(self):
        """Monitor browser and notify when closed"""
        try:
            while self.is_running and self.driver and self.driver.current_window_handle:
                sleep(1)
        except Exception:
            pass
        finally:
            if self.is_running:
                self.log_message.emit("Browser window closed")
                self.process_finished.emit()
    
    def stop(self):
        """Stop the worker thread"""
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.process_finished.emit()
    
    def url_changes(self, old_url):
        """Helper method to detect URL changes"""
        def _url_changes(driver):
            return driver.current_url != old_url
        return _url_changes

class InstallWorker(QThread):
    """Worker thread for installing dependencies"""
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    def run(self):
        self.status_update.emit("Installing dependencies...")
        self.log_message.emit("Starting dependency installation...")
        
        for module in REQUIRED_MODULES:
            try:
                __import__(module.replace('-', '_'))
                self.log_message.emit(f"✓ {module} already installed")
            except ImportError:
                self.log_message.emit(f"Installing {module}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                    self.log_message.emit(f"✓ {module} installed successfully")
                except subprocess.CalledProcessError as e:
                    self.log_message.emit(f"✗ Failed to install {module}: {e}")
        
        self.status_update.emit("Dependencies installation completed")
        self.log_message.emit("All dependencies processed")

class BuildWorker(QThread):
    """Worker thread for building executable"""
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    def run(self):
        self.status_update.emit("Building executable...")
        self.log_message.emit("Starting executable build...")
        
        current_os = platform.system().lower()
        try:
            if current_os == "windows" and os.path.exists(ICON_PATH_WINDOWS):
                cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", ICON_PATH_WINDOWS, 
                      __file__, "--name", APP_NAME]
            elif current_os == "darwin" and os.path.exists(ICON_PATH_MAC):
                cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", ICON_PATH_MAC, 
                      __file__, "--name", APP_NAME]
            elif current_os == "linux" and os.path.exists(ICON_PATH_LINUX):
                cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", ICON_PATH_LINUX, 
                      __file__, "--name", APP_NAME]
            else:
                cmd = ["pyinstaller", "--onefile", "--windowed", __file__, "--name", APP_NAME]
                self.log_message.emit(f"Note: Icon not found for {current_os}, using default")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message.emit("✓ Executable built successfully")
                self.status_update.emit("Build completed successfully")
            else:
                self.log_message.emit(f"✗ Build failed: {result.stderr}")
                self.status_update.emit("Build failed")
                
        except FileNotFoundError:
            self.log_message.emit("✗ PyInstaller not found. Please install it first.")
            self.status_update.emit("PyInstaller not found")

class IconWorker(QThread):
    """Worker thread for icon conversion"""
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str)
    
    def run(self):
        self.status_update.emit("Converting icon...")
        self.log_message.emit("Starting icon conversion for macOS...")
        
        try:
            from PIL import Image
            
            if not os.path.exists(ICON_PATH_WINDOWS):
                self.log_message.emit("✗ Source .ico file not found")
                self.status_update.emit("Source icon not found")
                return
            
            # Load the .ico file
            img = Image.open(ICON_PATH_WINDOWS)
            
            # Create icns directory structure
            icon_dir = os.path.dirname(ICON_PATH_MAC)
            if not os.path.exists(icon_dir):
                os.makedirs(icon_dir)
            
            # Save as .icns (PIL will handle the conversion)
            img.save(ICON_PATH_MAC, format='ICNS')
            
            self.log_message.emit("✓ Icon converted successfully to .icns format")
            self.status_update.emit("Icon conversion completed")
            
        except ImportError:
            self.log_message.emit("✗ Pillow library required for icon conversion")
            self.status_update.emit("Pillow library required")
        except Exception as e:
            self.log_message.emit(f"✗ Icon conversion failed: {e}")
            self.status_update.emit("Icon conversion failed")

class SidebarButton(QPushButton):
    """Custom styled sidebar button"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1f538d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #14375e;
            }
            QPushButton:checked {
                background-color: #14375e;
                font-weight: bold;
            }
        """)

class AutoBrightspaceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("AutoBrightspace - University Login Automation")
        self.resize(900, 700)
        
        # Set application icon based on platform
        if platform.system().lower() == "windows" and os.path.exists(ICON_PATH_WINDOWS):
            self.setWindowIcon(QIcon(ICON_PATH_WINDOWS))
        elif platform.system().lower() == "darwin" and os.path.exists(ICON_PATH_MAC):
            self.setWindowIcon(QIcon(ICON_PATH_MAC))
        elif platform.system().lower() == "linux" and os.path.exists(ICON_PATH_LINUX):
            self.setWindowIcon(QIcon(ICON_PATH_LINUX))
        
        # Initialize variables
        self.login_worker = None
        self.install_worker = None
        self.build_worker = None
        self.icon_worker = None
        
        # Set the dark theme
        self.set_dark_theme()
        
        # Create the main layout and widgets
        self.create_ui()
        
        # Load saved credentials
        self.load_credentials()
    
    def set_dark_theme(self):
        """Set a dark theme for the application"""
        dark_palette = QPalette()
        
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        
        QApplication.setPalette(dark_palette)
        
        # Set style sheet for various widgets
        QApplication.setStyle("Fusion")
        
        # Set application-wide stylesheet
        style = """
        QMainWindow, QWidget {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QFrame {
            border-radius: 5px;
            background-color: #383838;
        }
        QPushButton {
            background-color: #1f538d;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #14375e;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            color: white;
        }
        QLabel {
            color: #e0e0e0;
        }
        QComboBox {
            padding: 5px;
            background-color: #1f538d;
            color: white;
        }
        QComboBox QAbstractItemView {
            background-color: #383838;
            color: white;
            selection-background-color: #1f538d;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #404040;
            text-align: center;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #1f538d;
            border-radius: 4px;
        }
        """
        self.setStyleSheet(style)
    
    def create_ui(self):
        """Create the main user interface"""
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)
        
        # Create sidebar
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(200)
        sidebar_widget.setStyleSheet("background-color: #222222;")
        
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # App title in sidebar
        logo_label = QLabel("AutoBrightspace")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_label.setStyleSheet("color: #e0e0e0; margin-bottom: 15px;")
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons
        self.main_btn = SidebarButton("Main")
        self.main_btn.clicked.connect(lambda: self.switch_page(0))
        self.main_btn.setChecked(True)
        sidebar_layout.addWidget(self.main_btn)
        
        self.config_btn = SidebarButton("Configuration")
        self.config_btn.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.config_btn)
        
        self.setup_btn = SidebarButton("Setup & Build")
        self.setup_btn.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.setup_btn)
        
        self.shortcuts_btn = SidebarButton("Shortcuts")
        self.shortcuts_btn.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.shortcuts_btn)
        
        sidebar_layout.addStretch()
        
        # Scale factor selector
        scale_label = QLabel("UI Scale:")
        scale_label.setStyleSheet("color: #e0e0e0;")
        sidebar_layout.addWidget(scale_label)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["80%", "90%", "100%", "110%", "120%"])
        self.scale_combo.setCurrentIndex(2)  # 100% by default
        self.scale_combo.currentIndexChanged.connect(self.change_scale)
        sidebar_layout.addWidget(self.scale_combo)
        
        # Content area with stacked widget for "pages"
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #2d2d2d;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # Create the main pages
        self.create_main_page()
        self.create_config_page()
        self.create_setup_page()
        self.create_shortcuts_page()
        
        # Add to main layout
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(content_widget, 1)
    
    def create_main_page(self):
        """Create the main page with login controls"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Title area
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("AutoBrightspace")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Automated University Login with 2FA")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # Status area
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        
        status_title = QLabel("Status:")
        status_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        self.status_label = QLabel("Ready to login")
        self.status_label.setStyleSheet("color: #00CC66;")
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)
        
        # Buttons area
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(10, 10, 10, 10)
        
        self.login_button = QPushButton("Start Auto Login")
        self.login_button.setFixedHeight(42)
        self.login_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.login_button.clicked.connect(self.start_login)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedHeight(42)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #c93c3c;")
        self.stop_button.clicked.connect(self.stop_browser)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.stop_button)
        
        layout.addWidget(buttons_frame)
        
        # Log area
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        
        log_title = QLabel("Activity Log")
        log_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 10))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame, 1)
        
        self.stack.addWidget(page)
    
    def create_config_page(self):
        """Create the configuration page with credential settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # Configuration form
        config_frame = QFrame()
        config_layout = QVBoxLayout(config_frame)
        
        title_label = QLabel("Credentials Configuration")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        config_layout.addWidget(title_label)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        form_layout.addWidget(username_label, 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)
        
        # Password
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        # Secret Key
        secret_key_label = QLabel("2FA Secret Key:")
        self.secret_key_input = QLineEdit()
        form_layout.addWidget(secret_key_label, 2, 0)
        form_layout.addWidget(self.secret_key_input, 2, 1)
        
        config_layout.addLayout(form_layout)
        
        # Save button
        save_button = QPushButton("Save Configuration")
        save_button.setFixedWidth(250)
        save_button.setStyleSheet("background-color: #28a745;")
        save_button.clicked.connect(self.save_credentials)
        config_layout.addWidget(save_button, 0, Qt.AlignCenter)
        
        layout.addWidget(config_frame)
        
        # Help information
        help_frame = QFrame()
        help_layout = QVBoxLayout(help_frame)
        
        help_title = QLabel("Help")
        help_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        help_layout.addWidget(help_title)
        
        help_text = QLabel("""
How to get your 2FA Secret Key:
1. Visit the Leiden University Account Service.
2. Log in with your Leiden University credentials.
3. Navigate to Multi-Factor Authentication.
4. Select Enroll/Modify under TOTP Non-NetIQ Authenticator.
5. You will see ••••••••••••••• displayed under a QR code.
6. Click on the 👁️ (eye icon) to reveal your secret key.


Note: Your credentials are stored locally on your device.
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_frame, 1)
        
        self.stack.addWidget(page)
    
    def create_setup_page(self):
        """Create the setup page with dependencies and build options"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # Dependencies section
        deps_frame = QFrame()
        deps_layout = QVBoxLayout(deps_frame)
        
        deps_title = QLabel("Dependencies")
        deps_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        deps_layout.addWidget(deps_title)
        
        deps_button = QPushButton("Install Dependencies")
        deps_button.clicked.connect(self.install_dependencies)
        deps_layout.addWidget(deps_button)
        
        self.deps_status = QLabel("Click to check and install dependencies")
        deps_layout.addWidget(self.deps_status)
        
        layout.addWidget(deps_frame)
        
        # Build section
        build_frame = QFrame()
        build_layout = QVBoxLayout(build_frame)
        
        build_title = QLabel("Build Executable")
        build_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        build_layout.addWidget(build_title)
        
        build_button = QPushButton("Build Executable")
        build_button.clicked.connect(self.build_executable)
        build_layout.addWidget(build_button)
        
        self.build_status = QLabel("Build standalone executable for distribution")
        build_layout.addWidget(self.build_status)
        
        layout.addWidget(build_frame)
        
        # Icon conversion section (macOS only)
        if platform.system().lower() == "darwin":
            icon_frame = QFrame()
            icon_layout = QVBoxLayout(icon_frame)
            
            icon_title = QLabel("macOS Icon Conversion")
            icon_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
            icon_layout.addWidget(icon_title)
            
            icon_button = QPushButton("Convert Icon for macOS")
            icon_button.clicked.connect(self.convert_icon_for_mac)
            icon_layout.addWidget(icon_button)
            
            self.icon_status = QLabel("Convert .ico to .icns format for macOS")
            icon_layout.addWidget(self.icon_status)
            
            layout.addWidget(icon_frame)
        
        layout.addStretch()
        
        self.stack.addWidget(page)
    
    def create_shortcuts_page(self):
        """Create the shortcuts page for keyboard shortcut setup"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)
        
        # Title
        title_frame = QFrame()
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Keyboard Shortcuts")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Set up system-wide keyboard shortcuts to run AutoBrightSpace")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # Current OS detection
        current_os = platform.system().lower()
        os_frame = QFrame()
        os_layout = QVBoxLayout(os_frame)
        
        os_label = QLabel(f"Detected OS: {platform.system()}")
        os_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        os_layout.addWidget(os_label)
        
        layout.addWidget(os_frame)
        
        # Shortcut configuration
        shortcut_frame = QFrame()
        shortcut_layout = QVBoxLayout(shortcut_frame)
        
        # Shortcut key combination input
        shortcut_config_layout = QHBoxLayout()
        
        shortcut_label = QLabel("Shortcut Keys:")
        self.shortcut_input = QLineEdit()
        self.shortcut_input.setPlaceholderText("Ctrl+Shift+\\")
        self.shortcut_input.setText("Ctrl+Shift+\\")
        
        shortcut_config_layout.addWidget(shortcut_label)
        shortcut_config_layout.addWidget(self.shortcut_input)
        shortcut_layout.addLayout(shortcut_config_layout)
        
        # Setup button
        self.setup_shortcut_btn = QPushButton("Set Up Keyboard Shortcut")
        self.setup_shortcut_btn.setFixedHeight(42)
        self.setup_shortcut_btn.setStyleSheet("background-color: #28a745;")
        self.setup_shortcut_btn.clicked.connect(self.setup_keyboard_shortcut)
        shortcut_layout.addWidget(self.setup_shortcut_btn)
        
        # Status label
        self.shortcut_status = QLabel("Click the button above to set up your keyboard shortcut")
        shortcut_layout.addWidget(self.shortcut_status)
        
        layout.addWidget(shortcut_frame)
        
        # Instructions based on OS
        instructions_frame = QFrame()
        instructions_layout = QVBoxLayout(instructions_frame)
        
        instructions_title = QLabel("Instructions")
        instructions_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        instructions_layout.addWidget(instructions_title)
        
        if current_os == "linux":
            instructions_text = QLabel(r"""
<b>Linux (GNOME/KDE) Instructions:</b><br><br>

<b>Manual Setup (if automatic fails):</b><br>
1. Open Settings → Keyboard → Custom Shortcuts<br>
2. Click "+" to add a new shortcut<br>
3. Name: "AutoBrightSpace Quick Login"<br>
4. Command: <code>python /full/path/to/AutoBrightSpace.py run</code><br>
5. Set shortcut to: Ctrl+Shift+\<br><br>

<b>Alternative for different desktop environments:</b><br>
• <b>KDE:</b> System Settings → Shortcuts → Custom Shortcuts<br>
• <b>XFCE:</b> Settings → Keyboard → Application Shortcuts<br>
• <b>Command line:</b> Use tools like <code>xbindkeys</code> or <code>sxhkd</code>
            """)
        elif current_os == "darwin":  # macOS
            instructions_text = QLabel(r"""
<b>macOS Instructions:</b><br><br>

<b>Automatic Setup:</b><br>
• Click "Set Up Keyboard Shortcut" above<br>
• Follow the prompts to set up the shortcut<br><br>

<b>Manual Setup:</b><br>
1. Open System Preferences → Keyboard → Shortcuts<br>
2. Select "App Shortcuts" from the left sidebar<br>
3. Click "+" to add a new shortcut<br>
4. Application: "All Applications"<br>
5. Menu Title: Leave blank<br>
6. Keyboard Shortcut: Cmd+Shift+\<br><br>

<b>Alternative using Automator:</b><br>
1. Open Automator → New → Quick Action<br>
2. Add "Run Shell Script" action<br>
3. Shell: /bin/bash<br>
4. Script: <code>cd /path/to/AutoBrightSpace && python AutoBrightSpace.py run</code><br>
5. Save as "AutoBrightSpace Quick Login"<br>
6. Assign keyboard shortcut in System Preferences → Keyboard → Shortcuts → Services
            """)
        else:  # Windows
            instructions_text = QLabel(r"""
<b>Windows Instructions:</b><br><br>

<b>Automatic Setup:</b><br>
• Click "Set Up Keyboard Shortcut" above<br>
• A batch file will be created and shortcut instructions provided<br><br>

<b>Manual Setup using Task Scheduler:</b><br>
1. Open Task Scheduler (search in Start menu)<br>
2. Create Basic Task → Name: "AutoBrightSpace Hotkey"<br>
3. Trigger: "When I log on"<br>
4. Action: "Start a program"<br>
5. Program: <code>python</code><br>
6. Arguments: <code>AutoBrightSpace.py run</code><br>
7. Start in: <code>/path/to/AutoBrightSpace/</code><br><br>

<b>Alternative using AutoHotkey:</b><br>
1. Install AutoHotkey from autohotkey.com<br>
2. Create a .ahk script with:<br>
<code>^+\\::Run, python "C:\\path\\to\\AutoBrightSpace.py" run, C:\\path\\to\\</code><br>
3. Run the script or add to startup
            """)
        
        instructions_text.setWordWrap(True)
        instructions_text.setTextFormat(Qt.RichText)
        instructions_layout.addWidget(instructions_text)
        
        layout.addWidget(instructions_frame, 1)
        
        layout.addStretch()
        
        self.stack.addWidget(page)
    
    def setup_keyboard_shortcut(self):
        """Set up keyboard shortcut based on the operating system"""
        current_os = platform.system().lower()
        shortcut_keys = self.shortcut_input.text().strip()
        
        if not shortcut_keys:
            shortcut_keys = "Ctrl+Shift+\\"
        
        self.shortcut_status.setText("Setting up keyboard shortcut...")
        
        try:
            if current_os == "linux":
                self.setup_linux_shortcut(shortcut_keys)
            elif current_os == "darwin":
                self.setup_macos_shortcut(shortcut_keys)
            elif current_os == "windows":
                self.setup_windows_shortcut(shortcut_keys)
            else:
                self.shortcut_status.setText("❌ Unsupported operating system")
        except Exception as e:
            self.shortcut_status.setText(f"❌ Error setting up shortcut: {str(e)}")
            self.log_message(f"Shortcut setup error: {str(e)}")
    
    def setup_linux_shortcut(self, shortcut_keys):
        """Set up keyboard shortcut on Linux"""
        script_path = os.path.abspath(__file__)
        command = f"python {script_path} run"
        
        try:
            # Try GNOME first
            gsettings_result = subprocess.run([
                "gsettings", "set", "org.gnome.settings-daemon.plugins.media-keys",
                "custom-keybindings",
                "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/autobrightspace/']"
            ], capture_output=True, text=True)
            
            if gsettings_result.returncode == 0:
                # Set the shortcut details
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybindings:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/autobrightspace/",
                    "name", "AutoBrightSpace Quick Login"
                ])
                
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybindings:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/autobrightspace/",
                    "command", command
                ])
                
                # Convert shortcut format for GNOME
                gnome_shortcut = shortcut_keys.replace("Ctrl", "<Primary>").replace("Shift", "<Shift>").replace("\\", "backslash")
                subprocess.run([
                    "gsettings", "set",
                    "org.gnome.settings-daemon.plugins.media-keys.custom-keybindings:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/autobrightspace/",
                    "binding", gnome_shortcut
                ])
                
                self.shortcut_status.setText(f"✅ Keyboard shortcut set up successfully! Press {shortcut_keys} to run AutoBrightSpace")
                self.log_message(f"Linux keyboard shortcut configured: {shortcut_keys}")
            else:
                raise Exception("GNOME settings not available")
                
        except Exception as e:
            # Fallback: provide manual instructions
            self.shortcut_status.setText(f"""
❌ Automatic setup failed. Please set up manually:
1. Open Settings → Keyboard → Custom Shortcuts
2. Add new shortcut:
   • Name: AutoBrightSpace Quick Login
   • Command: {command}
   • Shortcut: {shortcut_keys}
            """)
            self.log_message(f"Linux shortcut auto-setup failed: {str(e)}")
    
    def setup_macos_shortcut(self, shortcut_keys):
        """Set up keyboard shortcut on macOS"""
        script_path = os.path.abspath(__file__)
        
        # Create an AppleScript that can be saved as an app
        applescript_content = f'''
tell application "Terminal"
    do script "cd '{os.path.dirname(script_path)}' && python '{os.path.basename(script_path)}' run"
end tell
'''
        
        # Save AppleScript
        applescript_path = os.path.join(os.path.dirname(script_path), "AutoBrightSpace_Shortcut.scpt")
        
        try:
            with open(applescript_path, 'w') as f:
                f.write(applescript_content)
            
            # Compile the AppleScript
            subprocess.run(["osacompile", "-o", applescript_path.replace('.scpt', '.app'), applescript_path])
            
            self.shortcut_status.setText(f"""
✅ Shortcut app created! To complete setup:
1. Open System Preferences → Keyboard → Shortcuts → Services
2. Find "AutoBrightSpace_Shortcut" in the list
3. Assign keyboard shortcut: {shortcut_keys.replace('Ctrl', 'Cmd')}

Or use the created app: AutoBrightSpace_Shortcut.app
            """)
            self.log_message(f"macOS shortcut app created at: {applescript_path.replace('.scpt', '.app')}")
            
        except Exception as e:
            self.shortcut_status.setText(f"""
❌ Automatic setup failed. Please set up manually:
1. Open Automator → New → Quick Action
2. Add "Run Shell Script" action
3. Script: cd {os.path.dirname(script_path)} && python {script_path} run
4. Save and assign shortcut in System Preferences
            """)
            self.log_message(f"macOS shortcut setup failed: {str(e)}")
    
    def setup_windows_shortcut(self, shortcut_keys):
        """Set up keyboard shortcut on Windows"""
        script_path = os.path.abspath(__file__)
        
        # Create a batch file for the shortcut
        batch_content = f'''@echo off
cd /d "{os.path.dirname(script_path)}"
python "{script_path}" run
pause
'''
        
        batch_path = os.path.join(os.path.dirname(script_path), "AutoBrightSpace_Shortcut.bat")
        
        try:
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Create a PowerShell script for setting up the hotkey
            ps_script = f'''
Add-Type -TypeDefinition @"
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;
public class GlobalHotkey
{{
    [DllImport("user32.dll")]
    public static extern bool RegisterHotKey(IntPtr hWnd, int id, int fsModifiers, int vlc);
    [DllImport("user32.dll")]
    public static extern bool UnregisterHotKey(IntPtr hWnd, int id);
    
    public static void RegisterAutobrightspaceHotkey()
    {{
        // This would require a more complex implementation
        Console.WriteLine("Hotkey registration would require a running application");
    }}
}}
"@
'''
            
            self.shortcut_status.setText(f"""
✅ Batch file created! To complete setup:

Option 1 - Using AutoHotkey (Recommended):
1. Install AutoHotkey from autohotkey.com
2. Create a .ahk file with this content:
   ^+\\::Run, "{batch_path}"
3. Run the .ahk script

Option 2 - Manual shortcut:
1. Right-click on AutoBrightSpace_Shortcut.bat
2. Create shortcut → Properties
3. Set shortcut key: {shortcut_keys}

Batch file created at: {batch_path}
            """)
            self.log_message(f"Windows batch file created: {batch_path}")
            
        except Exception as e:
            self.shortcut_status.setText(f"""
❌ Setup failed. Please create manually:
1. Create a .bat file with: python "{script_path}" run
2. Create a shortcut to the .bat file
3. Set shortcut key in Properties: {shortcut_keys}
            """)
            self.log_message(f"Windows shortcut setup failed: {str(e)}")
    
    def switch_page(self, index):
        """Switch between pages and update button states"""
        self.stack.setCurrentIndex(index)
        
        # Update button states
        self.main_btn.setChecked(index == 0)
        self.config_btn.setChecked(index == 1)
        self.setup_btn.setChecked(index == 2)
        self.shortcuts_btn.setChecked(index == 3)
    
    def change_scale(self, index):
        """Change UI scaling"""
        scale_factors = [0.8, 0.9, 1.0, 1.1, 1.2]
        if 0 <= index < len(scale_factors):
            # Note: Qt doesn't have built-in scaling like CustomTkinter
            # This would require actual implementation to scale fonts and controls
            # For now, we'll just show a message
            QMessageBox.information(self, "Scale Factor", 
                                   f"Scale factor set to {self.scale_combo.currentText()}\n"
                                   f"(Note: Would require application restart to take full effect)")
    
    def load_credentials(self):
        """Load saved credentials"""
        config = ConfigParser()
        if os.path.exists(CONFIG_PATH):
            config.read(CONFIG_PATH)
            self.username_input.setText(config.get('Credentials', 'username', fallback=''))
            self.password_input.setText(config.get('Credentials', 'password', fallback=''))
            self.secret_key_input.setText(config.get('Credentials', 'secret_key', fallback=''))
    
    def save_credentials(self):
        """Save credentials to config file"""
        config = ConfigParser()
        config['Credentials'] = {
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'secret_key': self.secret_key_input.text()
        }
        
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        
        QMessageBox.information(self, "Success", "Credentials saved successfully!")
        self.log_message("Credentials saved to configuration file")
    
    def start_login(self):
        """Start the login process"""
        username = self.username_input.text()
        password = self.password_input.text()
        secret_key = self.secret_key_input.text()
        
        if not all([username, password, secret_key]):
            QMessageBox.critical(self, "Error", "Please configure all credentials first!")
            return
        
        # Update UI state
        self.login_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(15)
        
        # Start worker thread
        self.login_worker = LoginWorker(username, password, secret_key)
        self.login_worker.status_update.connect(self.update_status)
        self.login_worker.progress_update.connect(lambda val: self.progress_bar.setValue(int(val * 100)))
        self.login_worker.log_message.connect(self.log_message)
        self.login_worker.process_finished.connect(self.reset_ui)
        self.login_worker.start()
    
    def stop_browser(self):
        """Stop the browser and login process"""
        if self.login_worker:
            self.login_worker.stop()
            self.log_message("Browser stopped by user")
    
    def reset_ui(self):
        """Reset UI after login process completes or is stopped"""
        self.login_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.login_worker = None
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.install_worker = InstallWorker()
        self.install_worker.status_update.connect(lambda msg: self.deps_status.setText(msg))
        self.install_worker.log_message.connect(self.log_message)
        self.install_worker.start()
    
    def build_executable(self):
        """Build executable using PyInstaller"""
        self.build_worker = BuildWorker()
        self.build_worker.status_update.connect(lambda msg: self.build_status.setText(msg))
        self.build_worker.log_message.connect(self.log_message)
        self.build_worker.start()
    
    def convert_icon_for_mac(self):
        """Convert .ico to .icns for macOS"""
        if hasattr(self, 'icon_status'):
            self.icon_worker = IconWorker()
            self.icon_worker.status_update.connect(lambda msg: self.icon_status.setText(msg))
            self.icon_worker.log_message.connect(self.log_message)
            self.icon_worker.start()
    
    def update_status(self, message, color="white"):
        """Update the status label with message and color"""
        color_map = {
            "green": "#00CC66",
            "red": "#FF5555",
            "yellow": "#FFCC00",
            "orange": "#FF9933",
            "blue": "#3399FF",
            "white": "#FFFFFF"
        }
        
        display_color = color_map.get(color.lower(), color)
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {display_color};")
    
    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_text.append(log_entry)
        # Auto-scroll to the bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Handle application closing"""
        # Stop browser if running
        if self.login_worker and self.login_worker.isRunning():
            self.login_worker.stop()
        
        # Call parent class close event
        super().closeEvent(event)

def load_credentials_cli():
    """Load credentials from config file for CLI use"""
    config = ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
        username = config.get('Credentials', 'username', fallback='')
        password = config.get('Credentials', 'password', fallback='')
        secret_key = config.get('Credentials', 'secret_key', fallback='')
        return username, password, secret_key
    return '', '', ''

def save_credentials_cli(username, password, secret_key):
    """Save credentials to config file for CLI use"""
    config = ConfigParser()
    config['Credentials'] = {
        'username': username,
        'password': password,
        'secret_key': secret_key
    }
    
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    
    print("✓ Credentials saved successfully!")

def cli_config():
    """CLI configuration mode"""
    print("=== AutoBrightSpace Configuration ===")
    print()
    
    # Load existing credentials
    username, password, secret_key = load_credentials_cli()
    
    print("Current credentials:")
    print(f"Username: {username if username else '(not set)'}")
    print(f"Password: {'*' * len(password) if password else '(not set)'}")
    print(f"2FA Secret: {'*' * len(secret_key) if secret_key else '(not set)'}")
    print()
    
    # Get new credentials
    new_username = input(f"Enter username [{username}]: ").strip()
    if not new_username:
        new_username = username
    
    import getpass
    new_password = getpass.getpass(f"Enter password [{'current' if password else 'not set'}]: ").strip()
    if not new_password:
        new_password = password
    
    new_secret_key = getpass.getpass(f"Enter 2FA secret key [{'current' if secret_key else 'not set'}]: ").strip()
    if not new_secret_key:
        new_secret_key = secret_key
    
    if new_username and new_password and new_secret_key:
        save_credentials_cli(new_username, new_password, new_secret_key)
        print()
        print("How to get your 2FA Secret Key:")
        print("1. Visit the Leiden University Account Service")
        print("2. Log in with your Leiden University credentials")
        print("3. Navigate to Multi-Factor Authentication")
        print("4. Select Enroll/Modify under TOTP Non-NetIQ Authenticator")
        print("5. Click on the 👁️ (eye icon) to reveal your secret key")
    else:
        print("✗ Configuration incomplete. Please provide all credentials.")

def cli_run():
    """CLI run mode - automated login without GUI"""
    print("=== AutoBrightSpace CLI Login ===")
    
    # Load credentials
    username, password, secret_key = load_credentials_cli()
    
    if not all([username, password, secret_key]):
        print("✗ Credentials not configured. Please run:")
        print("python AutoBrightSpace.py config")
        return False
    
    print(f"Starting automated login for user: {username}")
    
    try:
        # Initialize Chrome driver
        print("Initializing browser...")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        print("Navigating to Brightspace...")
        driver.get("https://brightspace.universiteitleiden.nl")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        current_url = driver.current_url
        
        # Handle SURFconext university selection page
        if current_url.startswith("https://engine.surfconext.nl/authentication/idp"):
            print("Selecting Leiden University...")
            try:
                leiden_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//div[@data-entityid='https://login.uaccess.leidenuniv.nl/nidp/saml2/metadata']"))
                )
                leiden_button.click()
                print("✓ Selected Leiden University")
                
                # Wait for page to change
                WebDriverWait(driver, 10).until(lambda d: d.current_url != current_url)
                current_url = driver.current_url
                
            except Exception as e:
                print(f"Failed to select Leiden University: {str(e)}")
                try:
                    submit_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//form[@action='https://engine.surfconext.nl/authentication/idp/process-wayf']//button[@type='submit']"))
                    )
                    submit_button.click()
                    print("✓ Used fallback method")
                    WebDriverWait(driver, 10).until(lambda d: d.current_url != current_url)
                    current_url = driver.current_url
                except Exception as e2:
                    print(f"✗ Both methods failed: {str(e2)}")
                    return False
        
        if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
            print("Entering credentials...")
            
            username_input = driver.find_element(By.NAME, "Ecom_User_ID")
            password_input = driver.find_element(By.NAME, "Ecom_Password")
            
            username_input.send_keys(username)
            password_input.send_keys(password)
            
            login_button = driver.find_element(By.ID, "loginbtn")
            login_button.click()
            
            WebDriverWait(driver, 10).until(lambda d: d.current_url != current_url)
            redirected_url = driver.current_url
            
            if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
                print("Processing 2FA...")
                
                next_button = driver.find_element(By.ID, "loginButton2")
                next_button.click()
                
                totp = pyotp.TOTP(secret_key)
                totp_code = totp.now()
                
                print(f"Generated TOTP code: {totp_code}")
                
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))
                code_input = driver.find_element(By.ID, "nffc")
                code_input.send_keys(totp_code)
                
                next_button_after_code = driver.find_element(By.ID, "loginButton2")
                next_button_after_code.click()
                
                print("✓ Login successful! Browser is ready to use.")
                print("Close the browser window when you're done.")
                
                # Keep the script running until browser is closed
                try:
                    while driver.current_window_handle:
                        sleep(1)
                except Exception:
                    pass
                
            else:
                print("✗ Login failed - check credentials")
                return False
                
        elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
            print("✓ Already logged in!")
            print("Browser is ready to use. Close the window when done.")
            
            # Keep running until browser is closed
            try:
                while driver.current_window_handle:
                    sleep(1)
            except Exception:
                pass
        else:
            print(f"? Unknown page detected: {current_url}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error during login: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='AutoBrightSpace - University Login Automation')
    parser.add_argument('mode', nargs='?', choices=['run', 'config'], 
                       help='CLI mode: "run" for automated login, "config" to set credentials')
    
    args = parser.parse_args()
    
    if args.mode == 'run':
        # CLI run mode
        success = cli_run()
        sys.exit(0 if success else 1)
    elif args.mode == 'config':
        # CLI config mode
        cli_config()
        sys.exit(0)
    else:
        # GUI mode (default)
        app = QApplication(sys.argv)
        window = AutoBrightspaceApp()
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
