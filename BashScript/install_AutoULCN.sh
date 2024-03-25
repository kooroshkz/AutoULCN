#!/bin/bash

# This script can help install the required packages and set up the TOTP script

# If you faced any issues, you can run the following commands manually by replacing correct shell rc file address

# For permission issues, run the following commands:
# sudo chmod +x ./totp_script.sh

# Install the required packages
echo "Installing required packages..."
sudo apt-get install -y oathtool xclip

# Copy the script to /usr/bin
echo "Copying the TOTP script to /usr/bin..."
sudo cp totp_script.sh /usr/bin

# Define the alias command
alias_command="alias totp='/usr/bin/totp_script.sh'"
alias_go_command="alias totpgo='/usr/bin/totp_script.sh && exit'"

# Determine the appropriate rc file based on the shell
rc_file="$HOME/.bashrc"
if [[ $SHELL == *zsh ]]; then
    rc_file="$HOME/.zshrc"
fi

# If you faced issue with wrong rc file, you can manually set the rc file by uncommenting the following lines
# rc_file="$HOME/.bashrc" # For bash
# rc_file="$HOME/.zshrc" # For zsh


# Add the alias to the appropriate rc file
echo "Adding aliases to $rc_file..."
echo "$alias_command" >> "$rc_file"
echo "$alias_go_command" >> "$rc_file"

# Reload the rc file
source ~/.bashrc 2>/dev/null
source ~/.zshrc 2>/dev/null


echo "Setup complete. You can now use 'totp' and 'totpgo' commands."