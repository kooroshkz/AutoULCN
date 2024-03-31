# Logged-in Brightspace Loader
## Python Non-Executable Version

## Setup
### Install requirements via
```bash
pip install -r requirements.txt
```

### Configure Credentials
There are two methods for this matter:
- Edit the file Credentials.txt.
- Hardcode into 'Brightspace.py' by following instructions via comments.

### Run
You can run Python script by 
```bash
python Brightspace.py
```

### Make it executable (Optional)
Install pyinstaller via
```bash
pip install pyinstaller
```
then run
```bash
pyinstaller --onefile --noconsole Brightspace.py
```

### Terminal alias and Shortcut (For Unix-like OS)
```bash
# After making Brightspace executable
sudo cp ./Brightspace /usr/bin
```

Add the following line to ~/.bashrc or ~/.zshrc
```bash
alias brightspace='(nohup /usr/bin/Brightspace 2>/dev/null >/dev/null &); exit'
```
Refresh via
```bash
source ~/.bashrc
# or
source ~/.zshhrc
```

Then for adding keyboard shortcut:

- Go to Settings -> Keyboard -> Shortcuts.
- Add a new shortcut from 'Custom Shortcuts'.
- Set the "Name" to "Run TOTP".
- In the "Command" field, enter:
```bash
    # For Bash
    gnome-terminal -- bash -i -c 'brightspace; exec bash'
    
    # For Zsh
    gnome-terminal -- zsh -i -c 'brightspace; exec zsh'
```


