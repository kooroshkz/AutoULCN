# AutoBrightspace

AutoBrightspace automates the login process to the Brightspace portal at Leiden University, handling both username/password authentication and two-factor authentication (2FA). The tool supports both GUI and CLI modes, configuration, automated login, and building standalone executables.

## Quick Start

### GUI Mode (Default)
Install dependencies and run the application:
```bash
pip install -r requirements.txt
python AutoBrightSpace.py
```
User Guide:
- From **Configuration** tab, set your username, password, and 2FA secret key.
- In **Main** tab, click "Start Auto Login" to perform the automated login.
- From **Setup & Build** tab, you can install dependencies and build standalone executables.
- In **Shortcuts** tab, you can set a keyboard shortcut for quick access.

### CLI Mode
For command-line usage:

**Configure/Change credentials:**
```bash
python AutoBrightSpace.py config
```

**Run automated login:**
```bash
python AutoBrightSpace.py run
```

**Build standalone executable:**
```bash
python AutoBrightSpace.py build
```

## Building Standalone Executables

AutoBrightspace can create single-file executables for Windows (.exe), macOS (.app), and Linux that work without requiring Python installation.

- **What Gets Created?** After building, you'll find in the `dist/` folder:

**Windows:**
- `AutoBrightspace.exe` - Main executable
- `AutoBrightspace_QuickLogin.bat` - Quick login launcher

**macOS:**
- `AutoBrightspace.app` - App bundle (double-clickable)
- `AutoBrightspace_QuickLogin.sh` - Quick login launcher  

**Linux:**
- `AutoBrightspace` - Executable file
- `AutoBrightspace_QuickLogin.sh` - Quick login launcher

## Getting Your 2FA Secret Key

1. Visit the [Leiden University Account Service](https://account.services.universiteitleiden.nl/).
2. Log in with your Leiden University credentials.
3. Navigate to **Login required** > **Multi-Factor Authentication** > log in and authenticate again.
4. Select **Enroll/Modify** under **TOTP Non-NetIQ Authenticator**.
5. You will see **•••••••••••••••** displayed under a QR code. Click on the **👁️ (eye icon)** to reveal your secret key.

## Troubleshooting

- **Credentials not working**: Make sure your username, password, and 2FA secret are correctly configured
- **Browser not opening**: Ensure Chrome is installed and ChromeDriver can be downloaded
- **2FA failing**: Verify your secret key is correct and try regenerating TOTP codes
- **Building executable fails**: Ensure you have `pyinstaller` installed and configured correctly
- **Shortcut not working**: Highly recommended to set a keyboard shortcut from system settings
- **Qt conflicts during build**: The build process automatically excludes conflicting Qt packages (PySide2, PyQt6)
- **Large executable size**: The ~80MB size is normal and includes all dependencies for standalone operation

## Advanced Usage

### Using the Enhanced Build Tool
For advanced building options:
```bash
# Use the standalone build tool
python build_tool.py

# Clean previous builds
python build_tool.py --clean
```

### Troubleshooting
- **ChromeDriver issues**: The issue is that `webdriver-manager` is trying to execute `THIRD_PARTY_NOTICES.chromedriver` instead of the actual chromedriver executable. This is a known bug with webdriver-manager. You can remove the `THIRD_PARTY_NOTICES.chromedriver` file from the `webdriver_manager\drivers` directory to resolve this issue. For MacOS/Linux run `rm -rf ~/.wdm` and for Windows run `rmdir /S /Q %USERPROFILE%\.wdm`.

## Security Notes

- **Encrypted Storage**: Credentials are encrypted using machine-specific keys before being stored locally
- **Local Storage Only**: All data remains on your device in your user data directory:
  - Linux: `~/.local/share/AutoBrightspace/`
  - macOS: `~/Library/Application Support/AutoBrightspace/`
  - Windows: `%LOCALAPPDATA%\AutoBrightspace\`
- **No External Transmission**: No data is transmitted to external servers