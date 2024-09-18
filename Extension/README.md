# AutoULCN Web Extension

AutoULCN simplifies Leiden University logins by generating and auto-filling a TOTP code. It securely stores your secret key and copies the TOTP code to the clipboard for seamless login.

## Installation

### Google Chrome (Recommended):
1. Download the extension folder.
2. Go to the Extensions page, enable **Developer mode**.
3. Select **Load unpacked** and choose the extension folder in `AutoULCN/Extension`

### Firefox:
#### Temporary Unpacked Version:
1. Open Firefox and go to `about:debugging`.
2. Click **This Firefox**, then **Load Temporary Add-on**.
3. Select any file inside the extension folder or the `.xpi` file.

#### Packaging for Firefox (.xpi):
1. In the project directory, run:
   ```
   zip -r AutoULCN.xpi .
   ```

## Extension Installation Tutorial:
[![Installation Tutorial](https://img.youtube.com/vi/Y_q0O2S5FNI/0.jpg)](https://www.youtube.com/watch?v=Y_q0O2S5FNI)

