#!/bin/bash

# The script uses oathtool and xclip, ensure they are installed

# In case install_AutoULCN.sh faced an issue, you can install the required packages manually by running the following commands:
# sudo apt-get install -y oathtool xclip

# Then copy this script to /usr/bin

# Add the following code to your ~/.bashrc file
# alias totp='/usr/bin/totp_script.sh && exit'

# If you face permission issues, you can run the following command:
# sudo chmod +x /usr/bin/totp_script.sh

# Replace <secret_key> with your secret key
totp=$(oathtool --totp -b <secret_key>)

# Copy the TOTP to clipboard
echo -n $totp | xclip -selection clipboard