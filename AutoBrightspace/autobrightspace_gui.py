import os
import platform
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyotp
import appdirs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser
from time import sleep

# List of dependencies to check and install
required_modules = ['pyotp', 'selenium', 'appdirs', 'pyinstaller', 'webdriver-manager', 'pillow']

app_name = "AutoBrightspace"
config_dir = appdirs.user_data_dir(app_name)
config_path = os.path.join(config_dir, 'config.ini')

# Path to the icon (assumed to be in the "icon" folder)
icon_path_windows = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.ico')
icon_path_mac = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.icns')

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

class AutoBrightspaceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoBrightspace - University Login Automation")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set icon if available
        if platform.system().lower() == "windows" and os.path.exists(icon_path_windows):
            self.root.iconbitmap(icon_path_windows)
        elif platform.system().lower() == "linux":
            # For Linux, try to use PNG icon if available
            png_icon = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.png')
            if os.path.exists(png_icon):
                icon = tk.PhotoImage(file=png_icon)
                self.root.iconphoto(False, icon)
        
        self.driver = None
        self.setup_ui()
        self.load_credentials()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Login")
        
        # Configuration tab
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="Configuration")
        
        # Setup tab
        setup_frame = ttk.Frame(notebook)
        notebook.add(setup_frame, text="Setup")
        
        self.setup_main_tab(main_frame)
        self.setup_config_tab(config_frame)
        self.setup_setup_tab(setup_frame)
        
    def setup_main_tab(self, parent):
        # Title
        title_label = ttk.Label(parent, text="AutoBrightspace", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(parent, text="Automated University Login with 2FA", font=("Arial", 10))
        subtitle_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Ready to login", foreground="green")
        self.status_label.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(10, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(pady=20)
        
        self.login_button = ttk.Button(buttons_frame, text="Start Auto Login", 
                                     command=self.start_login, style="Accent.TButton")
        self.login_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(buttons_frame, text="Stop", 
                                    command=self.stop_browser, state='disabled')
        self.stop_button.pack(side='left', padx=10)
        
        # Log frame
        log_frame = ttk.LabelFrame(parent, text="Log", padding="10")
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.log_text.pack(fill='both', expand=True)
        
    def setup_config_tab(self, parent):
        # Configuration form
        config_frame = ttk.LabelFrame(parent, text="Credentials Configuration", padding="20")
        config_frame.pack(fill='x', padx=20, pady=20)
        
        # Username
        ttk.Label(config_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(config_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(config_frame, text="Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(config_frame, textvariable=self.password_var, 
                                      show="*", width=40)
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Secret Key
        ttk.Label(config_frame, text="2FA Secret Key:").grid(row=2, column=0, sticky='w', pady=5)
        self.secret_key_var = tk.StringVar()
        self.secret_key_entry = ttk.Entry(config_frame, textvariable=self.secret_key_var, width=40)
        self.secret_key_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Save button
        save_button = ttk.Button(config_frame, text="Save Configuration", 
                               command=self.save_credentials)
        save_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Help text
        help_frame = ttk.LabelFrame(parent, text="Help", padding="10")
        help_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        help_text = """
How to get your 2FA Secret Key:
1. Go to your university's 2FA setup page
2. When setting up authenticator app, look for "manual entry" or "text code"
3. Copy the secret key (usually a long string of letters and numbers)
4. Paste it in the Secret Key field above

Note: Your credentials are stored locally and encrypted.
        """
        
        help_label = ttk.Label(help_frame, text=help_text, justify='left')
        help_label.pack(anchor='w')
        
    def setup_setup_tab(self, parent):
        # Dependencies frame
        deps_frame = ttk.LabelFrame(parent, text="Dependencies", padding="20")
        deps_frame.pack(fill='x', padx=20, pady=20)
        
        deps_button = ttk.Button(deps_frame, text="Install Dependencies", 
                               command=self.install_dependencies)
        deps_button.pack(pady=10)
        
        self.deps_status = ttk.Label(deps_frame, text="Click to check and install dependencies")
        self.deps_status.pack()
        
        # Build frame
        build_frame = ttk.LabelFrame(parent, text="Build Executable", padding="20")
        build_frame.pack(fill='x', padx=20, pady=20)
        
        build_button = ttk.Button(build_frame, text="Build Executable", 
                                command=self.build_executable)
        build_button.pack(pady=10)
        
        self.build_status = ttk.Label(build_frame, text="Build standalone executable for distribution")
        self.build_status.pack()
        
        # Icon conversion frame (macOS only)
        if platform.system().lower() == "darwin":
            icon_frame = ttk.LabelFrame(parent, text="macOS Icon Conversion", padding="20")
            icon_frame.pack(fill='x', padx=20, pady=20)
            
            icon_button = ttk.Button(icon_frame, text="Convert Icon for macOS", 
                                   command=self.convert_icon_for_mac)
            icon_button.pack(pady=10)
            
            self.icon_status = ttk.Label(icon_frame, text="Convert .ico to .icns format for macOS")
            self.icon_status.pack()
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def load_credentials(self):
        """Load saved credentials"""
        config = ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
            self.username_var.set(config.get('Credentials', 'username', fallback=''))
            self.password_var.set(config.get('Credentials', 'password', fallback=''))
            self.secret_key_var.set(config.get('Credentials', 'secret_key', fallback=''))
    
    def save_credentials(self):
        """Save credentials to config file"""
        config = ConfigParser()
        config['Credentials'] = {
            'username': self.username_var.get(),
            'password': self.password_var.get(),
            'secret_key': self.secret_key_var.get()
        }
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        messagebox.showinfo("Success", "Credentials saved successfully!")
        self.log_message("Credentials saved to configuration file")
    
    def install_dependencies(self):
        """Install required dependencies"""
        def install():
            self.deps_status.config(text="Installing dependencies...")
            self.log_message("Starting dependency installation...")
            
            for module in required_modules:
                try:
                    __import__(module.replace('-', '_'))
                    self.log_message(f"✓ {module} already installed")
                except ImportError:
                    self.log_message(f"Installing {module}...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                        self.log_message(f"✓ {module} installed successfully")
                    except subprocess.CalledProcessError as e:
                        self.log_message(f"✗ Failed to install {module}: {e}")
            
            self.deps_status.config(text="Dependencies installation completed")
            self.log_message("All dependencies processed")
        
        threading.Thread(target=install, daemon=True).start()
    
    def build_executable(self):
        """Build executable using PyInstaller"""
        def build():
            self.build_status.config(text="Building executable...")
            self.log_message("Starting executable build...")
            
            current_os = platform.system().lower()
            try:
                if current_os == "windows" and os.path.exists(icon_path_windows):
                    cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", icon_path_windows, 
                          "autobrightspace_gui.py", "--name", "AutoBrightspace"]
                elif current_os == "darwin" and os.path.exists(icon_path_mac):
                    cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", icon_path_mac, 
                          "autobrightspace_gui.py", "--name", "AutoBrightspace"]
                elif current_os == "linux":
                    cmd = ["pyinstaller", "--onefile", "--windowed", 
                          "autobrightspace_gui.py", "--name", "AutoBrightspace"]
                else:
                    self.log_message(f"Unsupported OS or icon not found: {current_os}")
                    self.build_status.config(text=f"Build failed: Unsupported OS")
                    return
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message("✓ Executable built successfully")
                    self.build_status.config(text="Build completed successfully")
                else:
                    self.log_message(f"✗ Build failed: {result.stderr}")
                    self.build_status.config(text="Build failed")
                    
            except FileNotFoundError:
                self.log_message("✗ PyInstaller not found. Please install it first.")
                self.build_status.config(text="PyInstaller not found")
        
        threading.Thread(target=build, daemon=True).start()
    
    def convert_icon_for_mac(self):
        """Convert .ico to .icns for macOS"""
        def convert():
            self.icon_status.config(text="Converting icon...")
            self.log_message("Starting icon conversion for macOS...")
            
            try:
                from PIL import Image
                
                if not os.path.exists(icon_path_windows):
                    self.log_message("✗ Source .ico file not found")
                    self.icon_status.config(text="Source icon not found")
                    return
                
                # Load the .ico file
                img = Image.open(icon_path_windows)
                
                # Create icns directory structure
                icon_dir = os.path.dirname(icon_path_mac)
                if not os.path.exists(icon_dir):
                    os.makedirs(icon_dir)
                
                # Save as .icns (PIL will handle the conversion)
                img.save(icon_path_mac, format='ICNS')
                
                self.log_message("✓ Icon converted successfully to .icns format")
                self.icon_status.config(text="Icon conversion completed")
                
            except ImportError:
                self.log_message("✗ Pillow library required for icon conversion")
                self.icon_status.config(text="Pillow library required")
            except Exception as e:
                self.log_message(f"✗ Icon conversion failed: {e}")
                self.icon_status.config(text="Icon conversion failed")
        
        threading.Thread(target=convert, daemon=True).start()
    
    def start_login(self):
        """Start the automated login process"""
        if not all([self.username_var.get(), self.password_var.get(), self.secret_key_var.get()]):
            messagebox.showerror("Error", "Please configure all credentials first!")
            return
        
        self.login_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress.start()
        
        def login_process():
            try:
                self.update_status("Initializing browser...", "blue")
                self.log_message("Starting automated login process")
                
                # Initialize Chrome driver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
                
                self.update_status("Navigating to login page...", "blue")
                self.log_message("Opening Brightspace login page")
                self.driver.get("https://brightspace.universiteitleiden.nl")
                
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                current_url = self.driver.current_url
                if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
                    self.update_status("Entering credentials...", "blue")
                    self.log_message("Entering username and password")
                    
                    username_input = self.driver.find_element(By.NAME, "Ecom_User_ID")
                    password_input = self.driver.find_element(By.NAME, "Ecom_Password")
                    
                    username_input.send_keys(self.username_var.get())
                    password_input.send_keys(self.password_var.get())
                    
                    login_button = self.driver.find_element(By.ID, "loginbtn")
                    login_button.click()
                    
                    WebDriverWait(self.driver, 10).until(self.url_changes(current_url))
                    redirected_url = self.driver.current_url
                    
                    if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
                        self.update_status("Handling 2FA...", "blue")
                        self.log_message("Processing two-factor authentication")
                        
                        next_button = self.driver.find_element(By.ID, "loginButton2")
                        next_button.click()
                        
                        totp = pyotp.TOTP(self.secret_key_var.get())
                        totp_code = totp.now()
                        
                        self.log_message(f"Generated TOTP code: {totp_code}")
                        
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))
                        code_input = self.driver.find_element(By.ID, "nffc")
                        code_input.send_keys(totp_code)
                        
                        next_button_after_code = self.driver.find_element(By.ID, "loginButton2")
                        next_button_after_code.click()
                        
                        self.update_status("Login successful! Browser ready", "green")
                        self.log_message("✓ Login completed successfully")
                    else:
                        self.update_status("Login failed - check credentials", "red")
                        self.log_message("✗ Login failed or incorrect credentials")
                        
                elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
                    self.update_status("Already logged in!", "green")
                    self.log_message("✓ Already logged in to Brightspace")
                else:
                    self.update_status("Unknown page detected", "orange")
                    self.log_message(f"? Unknown URL detected: {current_url}")
                
                # Keep browser open and monitor
                self.monitor_browser()
                
            except Exception as e:
                self.update_status(f"Error: {str(e)}", "red")
                self.log_message(f"✗ Error during login: {str(e)}")
                self.reset_ui()
        
        threading.Thread(target=login_process, daemon=True).start()
    
    def monitor_browser(self):
        """Monitor browser and reset UI when closed"""
        def monitor():
            try:
                while self.driver and self.driver.current_window_handle:
                    sleep(1)
            except Exception:
                pass
            finally:
                self.log_message("Browser window closed")
                self.root.after(0, self.reset_ui)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def stop_browser(self):
        """Stop browser and reset UI"""
        if self.driver:
            try:
                self.driver.quit()
                self.log_message("Browser stopped by user")
            except Exception:
                pass
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.login_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress.stop()
        self.update_status("Ready to login", "green")
        self.driver = None
    
    def url_changes(self, old_url):
        def _url_changes(driver):
            return driver.current_url != old_url
        return _url_changes
    
    def on_closing(self):
        """Handle application closing"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoBrightspaceGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
