import os
import platform
import subprocess
import sys
import threading
import datetime
import appdirs
import pyotp
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
    
    def set_light_theme(self):
        """Set a light theme for the application"""
        QApplication.setPalette(QApplication.style().standardPalette())
        QApplication.setStyle("Fusion")
        
        # Set application-wide stylesheet
        style = """
        QMainWindow, QWidget {
            background-color: #f0f0f0;
            color: #202020;
        }
        QFrame {
            border-radius: 5px;
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
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
            background-color: #cccccc;
            color: #888888;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            color: #202020;
        }
        QComboBox {
            padding: 5px;
            background-color: #1f538d;
            color: white;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: #202020;
            selection-background-color: #1f538d;
            selection-color: white;
        }
        QProgressBar {
            border: none;
            border-radius: 4px;
            background-color: #e0e0e0;
            text-align: center;
            color: #202020;
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
        
        sidebar_layout.addStretch()
        
        # Theme selector
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: #e0e0e0;")
        sidebar_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        sidebar_layout.addWidget(self.theme_combo)
        
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
1. Go to your university's 2FA setup page
2. When setting up authenticator app, look for "manual entry" or "text code"
3. Copy the secret key (usually a long string of letters and numbers)
4. Paste it in the Secret Key field above

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
    
    def switch_page(self, index):
        """Switch between pages and update button states"""
        self.stack.setCurrentIndex(index)
        
        # Update button states
        self.main_btn.setChecked(index == 0)
        self.config_btn.setChecked(index == 1)
        self.setup_btn.setChecked(index == 2)
    
    def change_theme(self, index):
        """Change application theme"""
        if index == 0:  # Dark theme
            self.set_dark_theme()
        else:  # Light theme
            self.set_light_theme()
    
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

def main():
    app = QApplication(sys.argv)
    window = AutoBrightspaceApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
