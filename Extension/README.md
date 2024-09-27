# AutoULCN Web Extension

<table>
  <tr>
    <td><img src="./images/icon128.png" width="70" alt="AutoULCN Icon"></td>
    <td>AutoULCN simplifies Leiden University logins by generating and copying a TOTP (Time-based One-Time Password) code to your clipboard. It securely stores your secret key and provides easy access to the TOTP code for a seamless login experience.</td>
  </tr>
</table>


## Installation

### Google Chrome:
1. Download and extract the project zip from [here](https://github.com/kooroshkz/AutoULCN/raw/main/Extension/AutoULCN.zip).
2. Go to the Extensions page by entering `chrome://extensions/` in the address bar or by selection in the menu.
3. Enable **Developer mode** by toggling the switch in the upper right corner.
4. Click **Load unpacked** and choose the extracted `AutoULCN` folder or `Extension` folder if you have downloaded the project repository.

### Firefox:

1. Open Firefox and select `Manage Extensions` or search `about:addons` in the address bar.
2. Click **Setting Button**, then **Install Add-on From File...**.
3. Download `AutoULCN.xpi` from [here](https://github.com/kooroshkz/AutoULCN/raw/main/Extension/AutoULCN.xpi) which can also be found in `/Extension/AutoULCN.xpi`.
4. Select `AutoULCN.xpi` to start using the extension on Firefox.
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
