# AutoBrightspace

AutoBrightspace automates the login process to the Brightspace portal at Leiden University, handling both username/password authentication and two-factor authentication (2FA). The tool supports configuration, running the automation, and building standalone executables for easier access.

## Setup Instructions

1. **Clone the repository**:

   If you haven't cloned the repository yet, run the following commands:

   ```bash
   git clone https://github.com/kooroshkz/AutoULCN.git
   cd AutoULCN/autobrightspace
   ```

2. **Install Dependencies**:
   Run the setup command to install all necessary Python dependencies.

   ```bash
   python autobrightspace.py --setup
   ```

3. **Configure User Credentials**:
   Set up or update your username, password, and 2FA secret key.

   ```bash
   python autobrightspace.py --configue
   ```

4. **Build an Executable** (Optional):
   Create a standalone executable for your platform (Windows, macOS, or Linux).

   ```bash
   python autobrightspace.py --build
   ```

## Keyboard Shortcuts

### For Linux Users:

If you are using Linux, you can follow these additional setup steps:

1. **Move AutoBrightspace to /opt**:

   ```bash
   sudo mv ~/Desktop/AutoULCN/AutoBrightspace/ /opt
   ```

   *(Replace `~/Desktop/AutoULCN` with the actual location if it was cloned somewhere else.)*

2. **Make the executable file executable**:

   ```bash
   sudo chmod +x /opt/AutoBrightspace/dist/AutoBrightspace
   ```

3. **Create a symlink for easy access**:

   ```bash
   sudo ln -sf /opt/AutoBrightspace/dist/AutoBrightspace /usr/local/bin/autobrightspace
   ```

4. **Run AutoBrightspace**:

   ```bash
   autobrightspace
   ```

5. **Optional: Set up a shortcut (GNOME Users)**:

   You can create a custom keyboard shortcut to quickly run AutoBrightspace. To do this, follow these steps:

   - Open the GNOME control center:

     ```bash
     gnome-control-center keyboard
     ```

   - Scroll down to "Custom Shortcuts" and click "+" to add a new shortcut.
   - Name it "AutoBrightspace".
   - For the command, use:

     ```bash
     autobrightspace
     ```

   - Click "Set Shortcut", then press `Ctrl+Shift+\`.
   - Click "Add" to save.

   Now, pressing `Ctrl+Shift+\` will launch AutoBrightspace.

## Available Commands

- **--setup**: Install all necessary dependencies.

   ```bash
   python autobrightspace.py --setup
   ```

- **--configue**: Configure or update your username, password, and 2FA secret key.

   ```bash
   python autobrightspace.py --configue
   ```

- **--run**: Run the program to automatically log in to Brightspace.

   ```bash
   python autobrightspace.py --run
   ```

- **--build**: Build a standalone executable for your operating system.

   ```bash
   python autobrightspace.py --build
   ```

- **--help**: Display a list of available commands and their descriptions.

   ```bash
   python autobrightspace.py --help
   ```
