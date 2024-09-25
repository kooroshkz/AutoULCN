# AutoULCN Web Extension

<table>
  <tr>
    <td><img src="./images/icon128.png" width="70" alt="AutoULCN Icon"></td>
    <td>AutoULCN simplifies Leiden University logins by generating and copying a TOTP (Time-based One-Time Password) code to your clipboard. It securely stores your secret key and provides easy access to the TOTP code for a seamless login experience.</td>
  </tr>
</table>


## Installation

### Google Chrome (Recommended):
1. Download the extension folder.
2. Go to the Extensions page by entering `chrome://extensions/` in the address bar.
3. Enable **Developer mode** by toggling the switch in the upper right corner.
4. Click **Load unpacked** and choose the `AutoULCN/Extension` folder.

### Firefox:

#### Temporary Unpacked Version:
1. Open Firefox and go to `about:debugging`.
2. Click **This Firefox**, then **Load Temporary Add-on**.
3. Select any file from the `AutoULCN/Extension` folder.

> **Notice**: A permanent version of the add-on will be available soon after review by the Firefox team.

---

## Setup and How to Use AutoULCN Extension

### Getting Your Secret Key

To set up the AutoULCN extension, you need to get your TOTP secret key from Leiden University's account service. Follow these steps:

1. Visit the [Leiden University Account Service](https://account.services.universiteitleiden.nl/).
2. Log in with your Leiden University credentials.
3. Navigate to **Login required** > **Multi-Factor Authentication** > log in and authenticate again.
4. Select **Enroll/Modify** under **TOTP Non-NetIQ Authenticator**.
5. You will see **•••••••••••••••** displayed under a QR code. Click on the **👁️ (eye icon)** to reveal your secret key.

The extension will automatically fetch the secret key when you click on the **👁️ (eye icon)** and display a green notification popup. If the key is not automatically fetched, you can manually copy the secret key and paste it into the extension:

1. Open the AutoULCN extension by clicking on the extension icon in your browser toolbar.
2. Paste the copied secret key into the input field provided and click **Save**.

### Using the Extension

1. Once you've saved your secret key, the extension will generate a TOTP code automatically whenever you visit the ULCN login pages.
2. The current TOTP code will be displayed in the extension popup. You can copy the code to your clipboard by clicking the **Copy** button in the extension.
3. Use the copied TOTP code to log in to any Leiden University service that requires two-factor authentication.

### Resetting Your Secret Key

If you need to reset or change your TOTP secret key:

1. Open the AutoULCN extension and click on the **⚙️ Settings** icon.
2. In the settings, click the **Reset Secret Key** button.
3. The extension will clear the saved key, and you will be prompted to enter a new key the next time you open the extension.

---

## Where and When to Use the Extension

- **ULCN Login Pages**: The extension is specifically designed for ULCN login pages such as [Leiden University login](https://login.uaccess.leidenuniv.nl) or [MFA services](https://mfa.services.universiteitleiden.nl).
- When you visit these pages, the extension will generate and copy the TOTP code for you, making it easy to paste into the login form.