### How to setup Script.py

##### Login to your [Account Services](https://account.services.universiteitleiden.nl/) and from 'Multi-factor Authentication' enable additional authentication methode.
##### You will face an QR-Code which you need to extract the 'Secret_Key' from.
##### You can use [ScanQR](https://scanqr.org/#scan) to get your Scanned Data in the following format:
- otpauth://totp/Leiden%20University:UL%5Cs**Student Number**?secret=**Secret_Key**&issuer=Leiden+University

##### Then you need to place the Key on Line 4 in between Columns ( '...' )
##### There you go! After running the script, the TOTP code will print as an output.