# Privacy Policy

**AutoULCN** is committed to protecting your privacy. This document outlines how your data is collected, used, and stored when you use the AutoULCN browser extension.

## Data Collection

AutoULCN does **not** collect, transmit, or share any personal data or information. The extension operates fully on your local device and interacts solely with your browser and local storage.

### Information Collected
The extension stores the following information **locally** on your device:
- **TOTP Secret Key**: This is used to generate Time-based One-Time Passwords (TOTP) for ULCN and MFA login forms. The secret key is stored in the browser’s local storage and is **never transmitted** or shared with any external servers or third parties.

## Data Usage

AutoULCN is designed to automate the process of logging into Leiden University's ULCN and MFA services by:
- Storing your TOTP secret key locally.
- Automatically generating and filling in the TOTP code during login.

This data is used solely for the purpose of providing automated login assistance. No personal data is accessed, transmitted, or used for any other purpose.

## Permissions

AutoULCN requests the following permissions:
- **activeTab**: To detect when the user is on a ULCN or MFA login page and automatically fill in the TOTP code.
- **storage**: To store the TOTP secret key locally on your device.
- **Host permissions**: To allow the extension to interact with the Leiden University login pages (`*://login.uaccess.leidenuniv.nl/*`, `*://mfa.services.universiteitleiden.nl/*`).

## Security

AutoULCN does not transmit or share any data with external servers. All sensitive information (such as the TOTP secret key) is stored locally on your device and is only used for the purposes of generating TOTP codes for authentication.

## Third-Party Access

AutoULCN does not sell, trade, or otherwise transfer to outside parties any of your personal information. No third-party access to your stored data is allowed.

## Changes to This Privacy Policy

This Privacy Policy may be updated periodically. Any changes will be reflected on this page, so please review it regularly.

## Contact Information

If you have any questions or concerns about this Privacy Policy, please contact us at:

**Koorosh Komeilizadeh**  
kkomeilizadeh@gmail.com  
kooroshkz.com
