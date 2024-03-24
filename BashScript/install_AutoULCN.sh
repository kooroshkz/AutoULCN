#!/bin/bash

# This script can help install the required packages and set up the TOTP script

# If you faced any issues, you can run the following commands manually.

# For permission issues, run the following commands:
# sudo chmod +x ./install_AutoULCN.sh

# Install the required packages.
sudo apt-get install -y oathtool xclip

# Copy the script to /usr/bin
sudo cp totp_script.sh /usr/bin

# Add the alias to the ~/.bashrc file

# The alias will allow you to run the script by typing 'totp' in the terminal
echo "alias totp='/usr/bin/totp_script.sh'" >> ~/.bashrc
# totpgo will run the script and exit the terminal, suitable for using as keyboard shortcut
echo "alias totpgo='/usr/bin/totp_script.sh && exit'" >> ~/.bashrc

# Reload the ~/.bashrc file
source ~/.bashrc