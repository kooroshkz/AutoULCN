## Extract Secret Key from QR code

1. Login to your [Account Services](https://account.services.universiteitleiden.nl/) and enable the additional authentication method called 'Non-NetIQ Authenticator'.
2. You will see a QR code that contains the 'Secret Key' you need to extract.
3. There are two approaches to extract the key:

     - **qrextr.py key extractor script**
     
         To run the script, make sure you have the following libraries installed:
         - opencv-python-headless
         - pyperclip
         - pillow
         - pyotp
         
         You can install them by running the following command in the current directory in the terminal:
         ```
         pip install -r requirements.txt
         ```

     - **Manually extracting the key**
     
         If you were unable to use the Python script via [ScanQR](https://scanqr.org/#scan), you can find your secret key in the following format:
         ```
         otpauth://totp/Leiden%20University:UL%5Cs**Student Number**?secret=**Secret_Key**&issuer=Leiden+University
         ```
         
         You can then use [TOTP Token Generator](https://totp.danhersam.com/) to generate your TOTP.
