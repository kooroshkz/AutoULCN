## AutoULCN Totp Generator using Bash

Easily add your TOTP to the clipboard using a Bash script by simply typing "TOTP" on Unix-like terminals.

### Step 1
Clone the project and replace '<secret_key>' with your actual Secret Key in 'totp_script.sh'.

```bash
nano totp_script.sh
```
You can use nano or any other text editor.

### Step 2
Run the installation script by executing:
```bash
./install_AutoULCN.sh
```

Now, whenever you type "totp" in the terminal, it will automatically run your script, generating the TOTP code and copying it to your clipboard.

Additionally, typing "totpgo" will close the terminal after execution, making this command suitable for use as a keyboard shortcut.

### Set Keyboard Shortcut

- Go to Settings -> Keyboard -> Shortcuts.
- Add a new shortcut from 'Custom Shortcuts'.
- Set the "Name" to "Run TOTP".
- In the "Command" field, enter:
```bash
    # For Bash
    gnome-terminal -- bash -i -c 'totpgo; exec bash'
    
    # For Zsh
    gnome-terminal -- zsh -i -c 'totpgo; exec zsh'
```
- Assign a key combination for this shortcut.
