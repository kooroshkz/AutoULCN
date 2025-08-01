# AutoBrightspace GUI Version

A modern graphical user interface for the AutoBrightspace university login automation tool.

## Features

- 🖥️ **Modern GUI**: Clean, tabbed interface built with tkinter
- 🔐 **Secure Credential Storage**: Local configuration with form-based input
- 🚀 **Automated 2FA**: Handles TOTP codes automatically
- 📊 **Real-time Logging**: View process status and logs in real-time
- 🔧 **Built-in Setup**: Install dependencies and build executables from GUI
- 🍎 **macOS Icon Support**: Automatic .ico to .icns conversion
- 🌍 **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Option 1: Using the GUI (Recommended)
1. Install Python 3.7+ 
2. Run the GUI version:
   ```bash
   python autobrightspace_gui.py
   ```
3. Go to the "Setup" tab and click "Install Dependencies"
4. Configure your credentials in the "Configuration" tab
5. Use "Start Auto Login" from the main tab

### Option 2: Manual Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python autobrightspace_gui.py
   ```

## Configuration

### Getting Your 2FA Secret Key
1. Go to your university's account settings
2. Find "Two-Factor Authentication" or "Security Settings"
3. When setting up a new authenticator app, look for:
   - "Manual Entry"
   - "Text Code" 
   - "Secret Key"
4. Copy the long alphanumeric string
5. Paste it into the GUI configuration

### First-Time Setup
1. **Configuration Tab**: Enter your username, password, and 2FA secret key
2. **Setup Tab**: Install dependencies and optionally build an executable
3. **Main Tab**: Start the automated login process

## Building Executables

### Windows
- Creates `AutoBrightspace.exe` with icon
- Uses `--windowed` flag to hide console

### macOS
- Automatically converts .ico to .icns format
- Creates `AutoBrightspace` app bundle
- Run icon conversion first if needed

### Linux
- Creates `AutoBrightspace` executable
- No icon support (standard for Linux)

## GUI Interface

### Main Tab
- **Status Display**: Shows current operation status
- **Progress Bar**: Visual feedback during operations
- **Start/Stop Buttons**: Control the automation process
- **Log Window**: Real-time logging with timestamps

### Configuration Tab
- **Credential Forms**: Secure input for username, password, 2FA key
- **Save Configuration**: Persist settings locally
- **Help Text**: Instructions for obtaining 2FA secret key

### Setup Tab
- **Dependency Installation**: One-click dependency management
- **Executable Building**: Create standalone applications
- **Icon Conversion** (macOS): Convert .ico to .icns format

## Security Features

- ✅ Local credential storage (no cloud/server)
- ✅ Password masking in GUI
- ✅ Secure config file handling
- ✅ Browser session monitoring
- ✅ Automatic cleanup on exit

## Troubleshooting

### Common Issues

**Chrome not found**
- Install Google Chrome browser
- The WebDriver Manager will handle ChromeDriver automatically

**Dependencies missing**
- Use the "Install Dependencies" button in Setup tab
- Or manually run: `pip install -r requirements.txt`

**macOS Icon issues**
- Use the "Convert Icon for macOS" button in Setup tab
- Or manually run: `python convert_icon.py`

**2FA codes not working**
- Verify your secret key is correct
- Check your device's time synchronization
- Try generating a new secret key

### Log Analysis
The GUI provides detailed logging to help diagnose issues:
- ✓ Green checkmarks indicate success
- ✗ Red X marks indicate errors  
- ? Yellow question marks indicate warnings
- Timestamps help track operation timing

## Command Line Version

The original command-line version (`autobrightspace.py`) is still available with these options:
- `python autobrightspace.py` - Run the program
- `python autobrightspace.py --setup` - Install dependencies
- `python autobrightspace.py --configure` - Configure credentials
- `python autobrightspace.py --build` - Build executable
- `python autobrightspace.py --help` - Show help

## Requirements

- Python 3.7+
- Google Chrome browser
- Internet connection
- Valid university credentials with 2FA setup

## Platform Support

| Platform | GUI | CLI | Executable | Icon |
|----------|-----|-----|------------|------|
| Windows  | ✅  | ✅  | ✅ (.exe)  | ✅   |
| macOS    | ✅  | ✅  | ✅ (.app)  | ✅   |
| Linux    | ✅  | ✅  | ✅         | ➖   |

## Contributing

This is an open-source project. Contributions welcome for:
- Additional browser support (Firefox, Safari)
- Enhanced security features
- UI/UX improvements
- Platform-specific optimizations

## License

Open source - feel free to modify and distribute according to your needs.
