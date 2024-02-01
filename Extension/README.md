# AutoULCN Web Extension

The extension is developed to prompt for your Secret Key, which is used to generate a TOTP code. After generating the code, it is automatically copied to the clipboard.

## For Google Chrome (Recommended):
- Download the extension directory.
- Enable developer mode from the Extension management page.
- Load the unpacked extension by selecting the directory.

## For Firefox:
- Temporary usage of the extension under development is possible.
- Run the following command via terminal in the project directory:
    ```
    zip -r AutoULCN.xpi .
    ```
- Open Firefox and go to the "about:debugging" page.
- Click on "This Firefox" in the left sidebar.
- Click on "Load Temporary Add-on."
- Navigate to and select your .xpi file.
