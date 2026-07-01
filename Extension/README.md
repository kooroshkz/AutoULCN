# AutoULCN Web Extension

<table>
  <tr>
    <td><img src="./images/icon128.png" width="70" alt="AutoULCN Icon"></td>
    <td>AutoULCN Web Extension simplifies Leiden University logins by generating and copying a TOTP (Time-based One-Time Password) code to your clipboard. It securely stores your secret key and provides easy access to the TOTP code for a seamless login.</td>
  </tr>
</table>

## <img src="https://www.google.com/chrome/static/images/chrome-logo.svg" alt="Chrome Logo" width="40" style="vertical-align:middle; margin-right:8px;"/> Google Chrome:

The project is easily accessible through Chrome Web Store from [this link](https://chromewebstore.google.com/detail/cjldiidhobimjehekbaolkhhlcjbmbkk?utm_source=item-share-cb).

## <img src="https://upload.wikimedia.org/wikipedia/commons/a/a0/Firefox_logo%2C_2019.svg" alt="Firefox Logo" width="40" style="vertical-align:middle; margin-right:8px;"/> Firefox:

Grab the signed `.xpi` from [here](https://github.com/kooroshkz/AutoULCN/raw/main/Extension/AutoULCN.xpi).
- Firefox will install it when you open the link. If it doesn't, follow these steps:
  - 1. Open Firefox `Add-ons and themes` (`about:addons`). From the top-right gear button, choose **Install Add-on From File...**.
  - 2. Select the downloaded `AutoULCN.xpi` file to install the extension.
- Note: installing the `.xpi` directly does **not** auto-update — use the Add-ons link above if you want automatic updates.

---

## Setup and Usage Instructions

### 1. Getting Your Secret Key

Download and install the AutoULCN extension from the Chrome Web Store or Firefox Add-ons page. Once installed, you need to set up your TOTP secret key to use the extension. University provides a TOTP secret key that you can use with the extension to generate the one-time password (OTP) required for two-factor authentication. For gaining access to your key, follow these steps:

1. Visit the [Leiden University Account Service](https://account.services.universiteitleiden.nl/).
2. Log in with your Leiden University credentials.
3. Navigate to **Login required** > **Multi-Factor Authentication** > log in and authenticate again.
4. Select **Enroll/Modify** under **TOTP Non-NetIQ Authenticator**.
5. You will see **•••••••••••••••** displayed under a QR code. Click on the **👁️ (eye icon)** to reveal your secret key.

### 2. Activation of the Extension

The extension will automatically fetch the secret key when you click on the **👁️ (eye icon)** and display a green notification popup. If the key is not automatically fetched, you can manually copy the secret key and paste it into the extension.

### 3. Backup and Best Practices

You can always still receive the code with email and SMS, but it is recommended to use Authenticator apps like Google Authenticator or Microsoft Authenticator as a backup when extension is not available. By scanning the QR code with these apps, you can ensure that you have a backup method for generating TOTP codes.

### 4. Using the Extension

1. Once you've saved your secret key, the extension will generate a TOTP code automatically whenever you visit the **ULCN login pages** such as [Leiden University login](https://login.uaccess.leidenuniv.nl) or [MFA services](https://mfa.services.universiteitleiden.nl).
2. The current TOTP code will be displayed in the extension popup. You can copy the code to your clipboard by clicking the **Copy** button in the extension.
3. You can reset the stored key or recover through extension settings by clicking the **⚙️ Settings** icon in the extension popup.

---

## For Developers

### Manual Installation from Source

If you want to contribute to the AutoULCN extension or modify it for your own use, you can install the extension from the source code:

1. Clone the repository:
   ```bash
   git clone https://github.com/kooroshkz/AutoULCN.git
   ```
2. Navigate to the `Extension` directory `AutoULCN/Extension`

3. Load the unpacked extension in your browser:
   - For Google Chrome, go to `chrome://extensions/`, enable **Developer mode**, and click **Load unpacked** to select the `Extension` folder.
   - For Firefox, go to `about:debugging#/runtime/this-firefox`, click **Load Temporary Add-on**, and select the `AutoULCN.xpi` file.

### File Structure

```
Extension/
├── manifest.json           # Chrome extension manifest (Manifest V3)
├── manifest.firefox.json   # Firefox extension manifest
├── popup.html              # Extension popup interface
├── popup.js                # Main popup logic and TOTP generation
├── content.js              # Content script for auto-detection
├── AutoULCN.xpi           # Firefox extension package
├── AutoULCN.zip           # Chrome extension package
├── dist/                   # Third-party libraries
└── images/                 # Extension icons
```

### Key Files Explanation

- **`manifest.json`** - Chrome extension configuration with permissions and content scripts
- **`manifest.firefox.json`** - Firefox-specific manifest with additional gecko settings
- **`popup.html`** - User interface for the extension popup with modern, clean design
- **`popup.js`** - Core functionality including TOTP generation, clipboard operations, and cross-browser compatibility
- **`content.js`** - Automatically detects and saves secret keys from Leiden University pages
- **`dist/jsOTP.min.js`** - Third-party library for generating Time-based One-Time Passwords (RFC 6238)

### Development Notes

- The extension uses **Manifest V3** for Chrome compatibility
- **Cross-browser support** for both Chrome and Firefox
- **Automatic secret key detection** on university authentication pages
- **Local storage** for secure key persistence
- **Modern UI design** matching Leiden University's color scheme

