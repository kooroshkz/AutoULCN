import os
import platform
import subprocess
import sys
import threading
import datetime
import customtkinter as ctk
from tkinter import messagebox, PhotoImage
import pyotp
import appdirs
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser
from time import sleep

# Set the appearance mode and default theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Set widget scaling higher for smoother UI on high DPI screens
ctk.set_widget_scaling(1.2)  # Increased scaling for smoother look
ctk.deactivate_automatic_dpi_awareness()  # Prevent Windows DPI scaling issues

# List of dependencies to check and install
required_modules = ['pyotp', 'selenium', 'appdirs', 'pyinstaller', 'webdriver-manager', 'pillow', 'customtkinter']

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
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set icon if available
        if platform.system().lower() == "windows" and os.path.exists(icon_path_windows):
            self.root.iconbitmap(icon_path_windows)
        elif platform.system().lower() == "linux":
            # For Linux, try to use PNG icon if available
            png_icon = os.path.join(os.getcwd(), 'icon', 'AutoBrightspace.png')
            if os.path.exists(png_icon):
                icon = PhotoImage(file=png_icon)
                self.root.iconphoto(False, icon)
        
        self.driver = None
        self.setup_ui()
        self.load_credentials()
        
    def setup_ui(self):
        # Create sidebar frame for navigation
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        
        # Logo/Title in sidebar
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="AutoBrightspace", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),  # Smoother font
            text_color=("#DCE4EE", "#DCE4EE")  # Consistent color in both themes
        )
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        # Define a common button style
        button_font = ctk.CTkFont(family="Segoe UI", size=14)  # Smoother, bigger font
        button_corner = 10  # More rounded corners for smoother edges
        button_height = 36
        button_fg = "#1f538d"
        button_hover = "#14375e"
        
        # Navigation buttons in sidebar
        self.main_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Main", 
            command=lambda: self.show_frame("main"),
            font=button_font,
            corner_radius=button_corner,
            height=button_height,
            fg_color=button_fg,
            hover_color=button_hover,
            border_width=0
        )
        self.main_button.pack(padx=20, pady=10, fill="x")
        
        self.config_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Configuration", 
            command=lambda: self.show_frame("config"),
            font=button_font,
            corner_radius=button_corner,
            height=button_height,
            fg_color=button_fg,
            hover_color=button_hover,
            border_width=0
        )
        self.config_button.pack(padx=20, pady=10, fill="x")
        
        self.setup_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Setup & Build", 
            command=lambda: self.show_frame("setup"),
            font=button_font,
            corner_radius=button_corner,
            height=button_height,
            fg_color=button_fg,
            hover_color=button_hover,
            border_width=0
        )
        self.setup_button.pack(padx=20, pady=10, fill="x")
        
        # Appearance mode selector
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Appearance Mode:", 
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#DCE4EE", "#DCE4EE")
        )
        self.appearance_mode_label.pack(padx=20, pady=(20, 0))
        
        self.appearance_mode_option = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=6,
            button_color="#1f538d",
            button_hover_color="#14375e",
            dropdown_hover_color="#14375e"
        )
        self.appearance_mode_option.pack(padx=20, pady=(10, 10), fill="x")
        self.appearance_mode_option.set("Dark")
        
        # Widget scaling
        self.scaling_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Widget Scaling:", 
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=("#DCE4EE", "#DCE4EE")
        )
        self.scaling_label.pack(padx=20, pady=(20, 0))
        
        self.scaling_option = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=12),
            corner_radius=6,
            button_color="#1f538d",
            button_hover_color="#14375e",
            dropdown_hover_color="#14375e"
        )
        self.scaling_option.pack(padx=20, pady=(10, 20), fill="x")
        self.scaling_option.set("100%")
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Create frames for each "tab"
        self.frames = {}
        
        # Main tab
        main_frame = ctk.CTkFrame(self.content_frame)
        self.frames["main"] = main_frame
        self.setup_main_tab(main_frame)
        
        # Configuration tab
        config_frame = ctk.CTkFrame(self.content_frame)
        self.frames["config"] = config_frame
        self.setup_config_tab(config_frame)
        
        # Setup tab
        setup_frame = ctk.CTkFrame(self.content_frame)
        self.frames["setup"] = setup_frame
        self.setup_setup_tab(setup_frame)
        
        # Show main frame initially
        self.show_frame("main")
        
    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Show selected frame
        self.frames[frame_name].pack(fill="both", expand=True)
        
    def change_appearance_mode(self, new_appearance_mode):
        # Set the new appearance mode
        ctk.set_appearance_mode(new_appearance_mode.lower())
        
        # Update status colors based on mode
        if self.status_label:
            current_text = self.status_label.cget("text")
            if "Ready" in current_text:
                self.status_label.configure(text_color="#00CC66")  # Bright green
            elif "Login successful" in current_text:
                self.status_label.configure(text_color="#00CC66")  # Bright green
            elif "failed" in current_text:
                self.status_label.configure(text_color="#FF5555")  # Bright red
            elif "Initializing" in current_text or "Navigating" in current_text or "Handling" in current_text:
                self.status_label.configure(text_color="#FFCC00")  # Bright yellow
        
    def change_scaling(self, new_scaling):
        # Apply new scaling
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
        
        # Force redraw to prevent rendering issues
        self.root.update()
        self.root.update_idletasks()
        
    def setup_main_tab(self, parent):
        # Title
        title_label = ctk.CTkLabel(
            parent, 
            text="AutoBrightspace", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=("#DCE4EE", "#DCE4EE")  # Consistent color in both themes
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            parent, 
            text="Automated University Login with 2FA", 
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#DCE4EE", "#DCE4EE")
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")  # Transparent for cleaner look
        status_frame.pack(fill="x", padx=20, pady=10)
        
        status_label = ctk.CTkLabel(
            status_frame, 
            text="Status:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=("#DCE4EE", "#DCE4EE")
        )
        status_label.pack(side="left", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Ready to login", 
            text_color="#00CC66",  # Brighter green for better visibility
            font=ctk.CTkFont(family="Segoe UI", size=13)
        )
        self.status_label.pack(side="left", padx=10, pady=10)
        
        # Progress bar
        progress_frame = ctk.CTkFrame(parent, fg_color="transparent")  # Transparent for cleaner look
        progress_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.progress = ctk.CTkProgressBar(
            progress_frame, 
            height=10,  # Slightly thinner for modern look
            corner_radius=4,  # Smoother corners
            progress_color="#1f538d",  # Match button color
            border_width=0  # No border for smoother look
        )
        self.progress.pack(fill="x", padx=10, pady=10)
        self.progress.set(0)  # Initially set to 0
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.pack(pady=20)
        
        self.login_button = ctk.CTkButton(
            buttons_frame, 
            text="Start Auto Login",
            command=self.start_login,
            width=200,
            height=42,
            corner_radius=10,  # Smoother corners
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e",
            border_width=0,  # No border for smoother look
            text_color="white",  # Ensure text is clearly visible
            text_color_disabled="gray"
        )
        self.login_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(
            buttons_frame, 
            text="Stop", 
            command=self.stop_browser, 
            state="disabled",
            width=100,
            height=42,
            corner_radius=10,  # Smoother corners
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color="#c93c3c",
            hover_color="#8b2020",
            border_width=0,  # No border for smoother look
            text_color="white",  # Ensure text is clearly visible
            text_color_disabled="gray"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Log frame
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame, 
            text="Activity Log", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=("#DCE4EE", "#DCE4EE")
        )
        log_label.pack(pady=(10, 5), anchor="w", padx=10)
        
        self.log_text = ctk.CTkTextbox(
            log_frame, 
            height=200, 
            font=ctk.CTkFont(family="Courier", size=12),  # Monospace font for log
            corner_radius=6,  # Smoother corners
            border_width=0,   # No border
            text_color=("#DCE4EE", "#DCE4EE"),  # Consistent text color
            scrollbar_button_color="#1f538d",  # Match button color
            scrollbar_button_hover_color="#14375e"  # Match button hover color
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
    def setup_config_tab(self, parent):
        # Configuration form
        config_frame = ctk.CTkFrame(parent)
        config_frame.pack(fill="x", padx=20, pady=20)
        
        config_title = ctk.CTkLabel(config_frame, text="Credentials Configuration", 
                                  font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"))
        config_title.pack(pady=(15, 20), padx=20)
        
        # Username
        username_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        username_frame.pack(fill="x", padx=20, pady=5)
        
        username_label = ctk.CTkLabel(username_frame, text="Username:", width=120, anchor="w")
        username_label.pack(side="left", padx=(0, 10))
        
        self.username_var = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(username_frame, textvariable=self.username_var, width=300)
        self.username_entry.pack(side="left", fill="x", expand=True)
        
        # Password
        password_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        password_frame.pack(fill="x", padx=20, pady=5)
        
        password_label = ctk.CTkLabel(password_frame, text="Password:", width=120, anchor="w")
        password_label.pack(side="left", padx=(0, 10))
        
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(password_frame, textvariable=self.password_var, 
                                        show="*", width=300)
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        # Secret Key
        secret_key_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        secret_key_frame.pack(fill="x", padx=20, pady=5)
        
        secret_key_label = ctk.CTkLabel(secret_key_frame, text="2FA Secret Key:", width=120, anchor="w")
        secret_key_label.pack(side="left", padx=(0, 10))
        
        self.secret_key_var = ctk.StringVar()
        self.secret_key_entry = ctk.CTkEntry(secret_key_frame, textvariable=self.secret_key_var, width=300)
        self.secret_key_entry.pack(side="left", fill="x", expand=True)
        
        # Save button
        save_button = ctk.CTkButton(
            config_frame, 
            text="Save Configuration",
            command=self.save_credentials,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        save_button.pack(pady=(20, 15))
        
        # Help text
        help_frame = ctk.CTkFrame(parent)
        help_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        help_title = ctk.CTkLabel(help_frame, text="Help", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"))
        help_title.pack(pady=(10, 5), anchor="w", padx=10)
        
        help_text = """
How to get your 2FA Secret Key:
1. Go to your university's 2FA setup page
2. When setting up authenticator app, look for "manual entry" or "text code"
3. Copy the secret key (usually a long string of letters and numbers)
4. Paste it in the Secret Key field above

Note: Your credentials are stored locally on your device.
        """
        
        help_label = ctk.CTkLabel(help_frame, text=help_text, justify="left")
        help_label.pack(anchor="w", padx=15, pady=10)
        
    def setup_setup_tab(self, parent):
        # Dependencies frame
        deps_frame = ctk.CTkFrame(parent)
        deps_frame.pack(fill="x", padx=20, pady=20)
        
        deps_title = ctk.CTkLabel(deps_frame, text="Dependencies", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"))
        deps_title.pack(pady=(10, 15), padx=10, anchor="w")
        
        deps_button = ctk.CTkButton(
            deps_frame, 
            text="Install Dependencies",
            command=self.install_dependencies,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        deps_button.pack(padx=15, pady=(0, 10))
        
        self.deps_status = ctk.CTkLabel(deps_frame, text="Click to check and install dependencies",
                                       font=ctk.CTkFont(family="Segoe UI", size=12))
        self.deps_status.pack(padx=15, pady=(0, 10))
        
        # Build frame
        build_frame = ctk.CTkFrame(parent)
        build_frame.pack(fill="x", padx=20, pady=20)
        
        build_title = ctk.CTkLabel(build_frame, text="Build Executable", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"))
        build_title.pack(pady=(10, 15), padx=10, anchor="w")
        
        build_button = ctk.CTkButton(
            build_frame, 
            text="Build Executable",
            command=self.build_executable,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        build_button.pack(padx=15, pady=(0, 10))
        
        self.build_status = ctk.CTkLabel(build_frame, text="Build standalone executable for distribution",
                                         font=ctk.CTkFont(family="Segoe UI", size=12))
        self.build_status.pack(padx=15, pady=(0, 10))
        
        # Icon conversion frame (macOS only)
        if platform.system().lower() == "darwin":
            icon_frame = ctk.CTkFrame(parent)
            icon_frame.pack(fill="x", padx=20, pady=20)
            
            icon_title = ctk.CTkLabel(icon_frame, text="macOS Icon Conversion", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"))
            icon_title.pack(pady=(10, 15), padx=10, anchor="w")
            
            icon_button = ctk.CTkButton(
                icon_frame, 
                text="Convert Icon for macOS",
                command=self.convert_icon_for_mac,
                height=38,
                corner_radius=10,
                font=ctk.CTkFont(family="Segoe UI", size=14)
            )
            icon_button.pack(padx=15, pady=(0, 10))
            
            self.icon_status = ctk.CTkLabel(icon_frame, text="Convert .ico to .icns format for macOS",
                                           font=ctk.CTkFont(family="Segoe UI", size=12))
            self.icon_status.pack(padx=15, pady=(0, 10))
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update()
    
    def update_status(self, message, color="white"):
        """Update status label with better color mapping"""
        # Map color names to more vibrant colors for better visibility
        color_map = {
            "green": "#00CC66",  # Bright green
            "red": "#FF5555",    # Bright red
            "yellow": "#FFCC00", # Bright yellow
            "orange": "#FF9933", # Bright orange
            "blue": "#3399FF",   # Bright blue
            "white": "#FFFFFF",  # White
        }
        
        # Use mapped color if available, otherwise use the provided color
        display_color = color_map.get(color.lower(), color)
        
        self.status_label.configure(text=message, text_color=display_color)
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
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        messagebox.showinfo("Success", "Credentials saved successfully!")
        self.log_message("Credentials saved to configuration file")
    
    def install_dependencies(self):
        """Install required dependencies"""
        def install():
            self.deps_status.configure(text="Installing dependencies...")
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
            
            self.deps_status.configure(text="Dependencies installation completed")
            self.log_message("All dependencies processed")
        
        threading.Thread(target=install, daemon=True).start()
    
    def build_executable(self):
        """Build executable using PyInstaller"""
        def build():
            self.build_status.configure(text="Building executable...")
            self.log_message("Starting executable build...")
            
            current_os = platform.system().lower()
            try:
                if current_os == "windows" and os.path.exists(icon_path_windows):
                    cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", icon_path_windows, 
                          __file__, "--name", "AutoBrightspace"]
                elif current_os == "darwin" and os.path.exists(icon_path_mac):
                    cmd = ["pyinstaller", "--onefile", "--windowed", "--icon", icon_path_mac, 
                          __file__, "--name", "AutoBrightspace"]
                elif current_os == "linux":
                    cmd = ["pyinstaller", "--onefile", "--windowed", 
                          __file__, "--name", "AutoBrightspace"]
                else:
                    self.log_message(f"Unsupported OS or icon not found: {current_os}")
                    self.build_status.configure(text=f"Build failed: Unsupported OS")
                    return
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_message("✓ Executable built successfully")
                    self.build_status.configure(text="Build completed successfully")
                else:
                    self.log_message(f"✗ Build failed: {result.stderr}")
                    self.build_status.configure(text="Build failed")
                    
            except FileNotFoundError:
                self.log_message("✗ PyInstaller not found. Please install it first.")
                self.build_status.configure(text="PyInstaller not found")
        
        threading.Thread(target=build, daemon=True).start()
    
    def convert_icon_for_mac(self):
        """Convert .ico to .icns for macOS"""
        def convert():
            self.icon_status.configure(text="Converting icon...")
            self.log_message("Starting icon conversion for macOS...")
            
            try:
                from PIL import Image
                
                if not os.path.exists(icon_path_windows):
                    self.log_message("✗ Source .ico file not found")
                    self.icon_status.configure(text="Source icon not found")
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
                self.icon_status.configure(text="Icon conversion completed")
                
            except ImportError:
                self.log_message("✗ Pillow library required for icon conversion")
                self.icon_status.configure(text="Pillow library required")
            except Exception as e:
                self.log_message(f"✗ Icon conversion failed: {e}")
                self.icon_status.configure(text="Icon conversion failed")
        
        threading.Thread(target=convert, daemon=True).start()
    
    def start_login(self):
        """Start the automated login process"""
        if not all([self.username_var.get(), self.password_var.get(), self.secret_key_var.get()]):
            messagebox.showerror("Error", "Please configure all credentials first!")
            return
        
        self.login_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress.start()
        self.progress.set(0.15)  # Show some initial progress
        
        def login_process():
            try:
                self.update_status("Initializing browser...", "yellow")
                self.log_message("Starting automated login process")
                
                # Initialize Chrome driver
                self.progress.set(0.3)
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
                
                self.update_status("Navigating to login page...", "yellow")
                self.log_message("Opening Brightspace login page")
                self.driver.get("https://brightspace.universiteitleiden.nl")
                
                self.progress.set(0.4)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                current_url = self.driver.current_url
                if current_url.startswith("https://login.uaccess.leidenuniv.nl"):
                    self.update_status("Entering credentials...", "yellow")
                    self.log_message("Entering username and password")
                    
                    username_input = self.driver.find_element(By.NAME, "Ecom_User_ID")
                    password_input = self.driver.find_element(By.NAME, "Ecom_Password")
                    
                    username_input.send_keys(self.username_var.get())
                    password_input.send_keys(self.password_var.get())
                    
                    self.progress.set(0.5)
                    login_button = self.driver.find_element(By.ID, "loginbtn")
                    login_button.click()
                    
                    WebDriverWait(self.driver, 10).until(self.url_changes(current_url))
                    redirected_url = self.driver.current_url
                    
                    if redirected_url.startswith("https://mfa.services.universiteitleiden.nl"):
                        self.update_status("Handling 2FA...", "yellow")
                        self.log_message("Processing two-factor authentication")
                        
                        self.progress.set(0.7)
                        next_button = self.driver.find_element(By.ID, "loginButton2")
                        next_button.click()
                        
                        totp = pyotp.TOTP(self.secret_key_var.get())
                        totp_code = totp.now()
                        
                        self.log_message(f"Generated TOTP code: {totp_code}")
                        
                        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "nffc")))
                        code_input = self.driver.find_element(By.ID, "nffc")
                        code_input.send_keys(totp_code)
                        
                        self.progress.set(0.9)
                        next_button_after_code = self.driver.find_element(By.ID, "loginButton2")
                        next_button_after_code.click()
                        
                        self.progress.set(1.0)
                        self.update_status("Login successful! Browser ready", "green")
                        self.log_message("✓ Login completed successfully")
                    else:
                        self.update_status("Login failed - check credentials", "red")
                        self.log_message("✗ Login failed or incorrect credentials")
                        
                elif current_url.startswith("https://brightspace.universiteitleiden.nl"):
                    self.progress.set(1.0)
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
        self.login_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress.stop()
        self.progress.set(0)
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
    root = ctk.CTk()
    app = AutoBrightspaceGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
