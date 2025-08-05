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

## Security Notes

- Credentials are stored locally in your user data directory
- 2FA secret keys are stored securely on your device
- No data is transmitted to external servers 
