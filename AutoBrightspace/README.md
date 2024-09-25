# AutoBrightspace

AutoBrightspace automates the login process to the Brightspace portal at Leiden University, handling both username/password authentication and two-factor authentication (2FA). The tool supports configuration, running the automation, and building standalone executables for easier access.

## Setup Instructions

1. **Clone the repository**:
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

## Available Commands

- **`--setup`**: Install all necessary dependencies.
   ```bash
   python autobrightspace.py --setup
   ```

- **`--configue`**: Configure or update your username, password, and 2FA secret key.
   ```bash
   python autobrightspace.py --configue
   ```

- **`--run`**: Run the program to automatically log in to Brightspace.
   ```bash
   python autobrightspace.py --run
   ```

- **`--build`**: Build a standalone executable for your operating system.
   ```bash
   python autobrightspace.py --build
   ```

- **`--help`**: Display a list of available commands and their descriptions.
   ```bash
   python autobrightspace.py --help