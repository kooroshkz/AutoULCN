## AutoULCN Totp Generator using Bash

Easily add your TOTP to the clipboard using a Bash script by simply typing "TOTP" on Linux terminals.

### Step 1
Install oathtool
```bash
sudo apt-get install oathtool
```

### Step 2
Edit totp_script.sh by replacing your secret_key and then move the file to /usr/bin by
```bash
sudo mv totp_script.sh /usr/bin
```

### Step 3
- Open your .bashrc or .bash_aliases file. You can use a text editor like nano or vim. For example:

```bash
nano ~/.bashrc
```
Add the following line at the end of the file:

```bash
alias totp='/usr/bin/totp_script.sh && exit'
```

Save the file and exit the text editor.

Run the following command to apply the changes:

```bash
source ~/.bashrc
```
Now, whenever you type "totp" in the terminal, it will automatically run your script, generating the TOTP code and copying it to your clipboard before closing the terminal.

### Set Keyboard Shortcut

- Go to Settings -> Keyboard -> Shortcuts.
- Add a new shortcut.
- Set the "Name" to whatever you like, for example, "Run TOTP".
- In the "Command" field, enter:
```bash
    gnome-terminal -- bash -i -c 'totp; exec bash'
```
- Assign a key combination for this shortcut.