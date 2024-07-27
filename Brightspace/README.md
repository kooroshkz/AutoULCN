# Logged-in Brightspace Loader

## Project Details

**Brightspace.py:**  
This script automates the login process for Brightspace using Selenium. Credentials are securely stored within the script itself.

**For updating credentials:**
The credentials are stored in a configuration file named `config.ini`, which is located in a directory specific to the application. The location of this directory varies depending on the operating system:

- **Windows:** `C:\Users\<Username>\AppData\Local\AUTOULCN\config.ini`
- **macOS:** `~/Library/Application Support/AUTOULCN/config.ini`
- **Linux:** `~/.local/share/AUTOULCN/config.ini`

The directory and file are automatically created if they do not exist, and the credentials are updated whenever the script is run.

## Python Non-Executable Version

### Setup

#### 1. Install Requirements
Install the required packages by running:
```bash
pip install -r requirements.txt
```

#### 2. Configure Credentials
Set up your credentials directly within the script by following the comments provided in `Brightspace.py`. This approach simplifies the process by avoiding external files.

### Run
To run the script, use:
```bash
python Brightspace.py
```

### Optional: Make it Executable
To convert the script into an executable, first install PyInstaller:
```bash
pip install pyinstaller
```
Then create the executable:
```bash
pyinstaller --onefile --noconsole Brightspace.py
```

### Optional: Create Terminal Alias and Shortcut (For Unix-like OS)
To easily run the executable, you can create a terminal alias and keyboard shortcut:

1. **Copy Executable to `/usr/bin`:**
   ```bash
   sudo cp ./Brightspace /usr/bin
   ```

2. **Add Alias to `.bashrc` or `.zshrc`:**
   ```bash
   alias brightspace='(nohup /usr/bin/Brightspace 2>/dev/null >/dev/null &); exit'
   ```

3. **Refresh Shell Configuration:**
   ```bash
   source ~/.bashrc
   # or
   source ~/.zshrc
   ```

4. **Add Keyboard Shortcut:**
   - Go to `Settings` -> `Keyboard` -> `Shortcuts`.
   - Add a new shortcut under `Custom Shortcuts`.
   - Set "Name" to "Run Brightspace" and "Command" to:
     ```bash
     # For Bash
     gnome-terminal -- bash -i -c 'brightspace; exec bash'
     
     # For Zsh
     gnome-terminal -- zsh -i -c 'brightspace; exec zsh'
     ```