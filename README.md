# AutoULCN

In this open-source project, we aim to implement a swift and secure two-step verification auto-filler for Leiden University Login Web pages.

<img src="Files/msf.png" alt="MSF" width="400">

## Solutions
- Browser Extention to auto-fill Credentials
- Python script to load Brightspace Logged-in
- TOTP (6-digit code) Generator web-based
- Bash TOTP Generator with a keyboard shortcut
- What else? You say ...

## How to start?

### Setup Video

[![AutoULCN Setup Guide](Files/cover.png)](https://youtu.be/52kdsJtcGTY)
Click <a href="https://youtu.be/52kdsJtcGTY">here</a> to watch setup tutorial video

### Setup Guide

We use the Non-NetIQ Authentication method to gain access to your Secret_Key to be able to generate and auto-fill the 6-digit key called TOTP (Time-based one-time password)

Keep in mind the first step would be the hardest so keep an eye on the documentation and videos.

### Step 1
Log in and gain access to <a href="https://account.services.universiteitleiden.nl/">Account service</a> and select 'Multi-Factor Authentication'.

<img src="Files/account_service.png" alt="MSF" width="500">

### Step 2
Enroll or Modify for 'Non-NetIQ Authenticator'

The story is about the QR-Code in front of you, your Secret_Key is embedded in this QR so you can Extract the key via
- 'AutoULCN Key_extractor' available from the above directories
- Manually extracting the key by <a href="https://scanqr.org/#scan)">Qr-Reader</a> and you can find your secret key in the following format:
```
otpauth://totp/Leiden%20University:UL%5Cs**Student Number**?secret=**Secret_Key**&issuer=Leiden+University
```
As a backup always use a Third-Party authenticator as well like:
- <a href="https://scanqr.org/#scan">Google Authenticator</a>
- <a href="https://scanqr.org/#scan">Microsoft Authenticator</a>

### Step 3
After setting up this authentication method by entering your generated TOTP we are ready to use AutoULCN

### Step 4

Now choose your preferred AutoULCN Method from the directories above:

- **Chrome Extention**: An initial local version of the extension that will locally store your secret_key for generating and copying the TOTP code

<img src="Files/Extention_Preview.gif" alt="MSF" width="500">

- **Brightspace**: A Python script that running Selenium and auto-filling your

<img src="Files/Brightspace_Preview.gif" alt="MSF" width="450">

- **Bash Script**: Install totp generator as bash script on your shell

 <img src="Files/Bash_Preview.png" alt="MSF" width="400">

## Contribution

You're always welcome to send pull requests by Forking Repository and add a new feature or help fix the code issues.
