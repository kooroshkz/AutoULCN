#!/usr/bin/env python3
"""
Build script for AutoBrightspace
Creates single-file executables for Windows, macOS, and Linux
"""

import os
import sys
import platform
import subprocess
import shutil
import tempfile
from pathlib import Path

class AutoBrightspaceBuildTool:
    def __init__(self, source_file="AutoBrightSpace.py"):
        self.source_file = Path(source_file).resolve()
        self.project_dir = self.source_file.parent
        self.app_name = "AutoBrightspace"
        self.current_os = platform.system().lower()
        
        # Output directories
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        
        # Icon paths
        self.icon_dir = self.project_dir / "icon"
        self.icon_paths = {
            "windows": self.icon_dir / "AutoBrightspace.ico",
            "darwin": self.icon_dir / "AutoBrightspace.icns",
            "linux": self.icon_dir / "AutoBrightspace.png"
        }
        
        # Executable names for different platforms
        self.executable_names = {
            "windows": f"{self.app_name}.exe",
            "darwin": self.app_name,
            "linux": self.app_name
        }
    
    def create_missing_icons(self):
        """Create missing icons from existing ones or generate defaults"""
        icons_created = False
        
        try:
            from PIL import Image
            
            # Check which icons we have and which we need
            existing_icons = {}
            for platform, icon_path in self.icon_paths.items():
                if icon_path.exists():
                    existing_icons[platform] = icon_path
                    print(f"✓ Found existing {platform} icon: {icon_path.name}")
            
            # If we have no icons at all, create default ones
            if not existing_icons:
                print("No existing icons found, creating default icons...")
                return self.create_default_icons()
            
            # Create missing PNG for Linux if we have ICO or ICNS
            if "linux" not in existing_icons and ("windows" in existing_icons or "darwin" in existing_icons):
                print("Creating PNG icon for Linux from existing icon...")
                
                # Try to convert from ICO first, then ICNS
                source_icon = existing_icons.get("windows") or existing_icons.get("darwin")
                if source_icon:
                    try:
                        img = Image.open(source_icon)
                        # Convert to RGBA if needed
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        # Save as PNG
                        img.save(self.icon_paths["linux"], "PNG")
                        print(f"✓ Created PNG icon from {source_icon.name}: {self.icon_paths['linux']}")
                        icons_created = True
                    except Exception as e:
                        print(f"⚠ Could not convert icon to PNG: {e}")
            
            # Create missing ICO for Windows if we have PNG or ICNS
            if "windows" not in existing_icons and ("linux" in existing_icons or "darwin" in existing_icons):
                print("Creating ICO icon for Windows from existing icon...")
                
                source_icon = existing_icons.get("linux") or existing_icons.get("darwin")
                if source_icon:
                    try:
                        img = Image.open(source_icon)
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        img.save(self.icon_paths["windows"], "ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                        print(f"✓ Created ICO icon from {source_icon.name}: {self.icon_paths['windows']}")
                        icons_created = True
                    except Exception as e:
                        print(f"⚠ Could not convert icon to ICO: {e}")
            
            # Create missing ICNS for macOS if we have PNG or ICO  
            if "darwin" not in existing_icons and ("linux" in existing_icons or "windows" in existing_icons):
                print("Creating ICNS icon for macOS from existing icon...")
                
                source_icon = existing_icons.get("linux") or existing_icons.get("windows")
                if source_icon:
                    try:
                        img = Image.open(source_icon)
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        img.save(self.icon_paths["darwin"], "ICNS")
                        print(f"✓ Created ICNS icon from {source_icon.name}: {self.icon_paths['darwin']}")
                        icons_created = True
                    except Exception as e:
                        print(f"⚠ Could not convert icon to ICNS: {e}")
                        # Create PNG fallback for macOS
                        try:
                            img.save(self.icon_paths["darwin"].with_suffix(".png"), "PNG")
                            print(f"✓ Created PNG fallback for macOS: {self.icon_paths['darwin'].with_suffix('.png')}")
                            icons_created = True
                        except Exception as e2:
                            print(f"⚠ Could not create PNG fallback: {e2}")
            
            return icons_created or bool(existing_icons)
            
        except ImportError:
            print("⚠ PIL/Pillow not available for icon conversion")
            print("✓ Will use existing icons as-is")
            return bool(existing_icons)
        except Exception as e:
            print(f"⚠ Error processing icons: {e}")
            print("✓ Will use existing icons as-is")
            return bool(existing_icons)
    
    def create_default_icons(self):
        """Create simple default icons from scratch"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple 256x256 icon
            img = Image.new('RGBA', (256, 256), (31, 83, 141, 255))  # Blue background
            draw = ImageDraw.Draw(img)
            
            # Draw a simple "AB" text
            try:
                # Try to use a decent font
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 120)
                except:
                    font = ImageFont.load_default()
            
            # Center the text
            text = "AB"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (256 - text_width) // 2
            y = (256 - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
            
            # Save in different formats
            self.icon_dir.mkdir(exist_ok=True)
            
            # PNG for Linux
            img.save(self.icon_paths["linux"], "PNG")
            print(f"✓ Created PNG icon: {self.icon_paths['linux']}")
            
            # ICO for Windows
            img.save(self.icon_paths["windows"], "ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"✓ Created ICO icon: {self.icon_paths['windows']}")
            
            # ICNS for macOS (requires pillow-heif or other plugins)
            try:
                img.save(self.icon_paths["darwin"], "ICNS")
                print(f"✓ Created ICNS icon: {self.icon_paths['darwin']}")
            except Exception as e:
                print(f"⚠ Could not create ICNS icon: {e}")
                # Copy PNG as fallback
                shutil.copy2(self.icon_paths["linux"], self.icon_paths["darwin"].with_suffix(".png"))
                print(f"✓ Created PNG fallback for macOS: {self.icon_paths['darwin'].with_suffix('.png')}")
            
            return True
            
        except ImportError:
            print("⚠ PIL/Pillow not available for icon creation")
            return False
        except Exception as e:
            print(f"⚠ Error creating icons: {e}")
            return False
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        print("Checking build dependencies...")
        
        missing_deps = []
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"✓ PyInstaller {PyInstaller.__version__} available")
        except ImportError:
            missing_deps.append("pyinstaller")
        
        # Check and prepare icons
        print("Checking application icons...")
        if not self.create_missing_icons():
            print("⚠ No icons available, will build without icon")
        
        if missing_deps:
            print(f"✗ Missing dependencies: {', '.join(missing_deps)}")
            print("Install them with: pip install " + " ".join(missing_deps))
            return False
        
        return True
    
    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("Cleaning previous build files...")
        
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✓ Cleaned {dir_path}")
        
        # Also clean spec files
        for spec_file in self.project_dir.glob("*.spec"):
            spec_file.unlink()
            print(f"✓ Cleaned {spec_file}")
    
    def create_pyinstaller_spec(self):
        """Create a detailed PyInstaller spec file"""
        current_icon = self.icon_paths.get(self.current_os)
        icon_path = str(current_icon) if current_icon and current_icon.exists() else None
        
        # If macOS and .icns doesn't exist but .png does, use the .png
        if self.current_os == "darwin" and not current_icon.exists():
            png_fallback = current_icon.with_suffix(".png")
            if png_fallback.exists():
                icon_path = str(png_fallback)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.source_file}'],
    pathex=['{self.project_dir}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'webdriver_manager',
        'webdriver_manager.chrome',
        'pyotp',
        'cryptography',
        'cryptography.fernet',
        'appdirs'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'PySide2',
        'PySide6', 
        'PyQt6',
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL.ImageTk',
        'PIL.ImageQt',
        'IPython',
        'jupyter',
        'notebook',
        'jupyterlab',
        'sphinx',
        'babel',
        'pytest',
        'astroid'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out unnecessary files
a.datas = [x for x in a.datas if not x[0].startswith('tcl')]
a.datas = [x for x in a.datas if not x[0].startswith('tk')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.executable_names[self.current_os]}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # THIS CREATES A SINGLE FILE!
    {f'icon="{icon_path}",' if icon_path else '# No icon specified'}
)
'''
        
        # Add macOS app bundle creation
        if self.current_os == "darwin":
            spec_content += f'''
app = BUNDLE(
    exe,
    name='{self.app_name}.app',
    icon='{icon_path if icon_path else ""}',
    bundle_identifier='com.autobrightspace.app',
    info_plist={{
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'AutoBrightspace',
        'CFBundleDocumentTypes': [],
        'CFBundleExecutable': '{self.app_name}',
        'CFBundleName': '{self.app_name}',
        'CFBundleDisplayName': 'AutoBrightspace',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSRequiresAquaSystemAppearance': 'False'
    }}
)
'''
        
        spec_file = self.project_dir / f"{self.app_name}.spec"
        spec_file.write_text(spec_content)
        print(f"✓ Created spec file: {spec_file}")
        return spec_file
    
    def build_executable(self):
        """Build the executable using PyInstaller"""
        if not self.check_dependencies():
            return False
        
        print(f"Building executable for {self.current_os}...")
        self.clean_build_dirs()
        
        try:
            # Create spec file
            spec_file = self.create_pyinstaller_spec()
            
            # Run PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, 
                                  cwd=self.project_dir,
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode != 0:
                print(f"✗ PyInstaller failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("✓ PyInstaller completed successfully")
            
            # Post-processing
            self.post_process_executable()
            
            # Clean up build artifacts for a cleaner result
            self.cleanup_build_artifacts()
            
            return True
            
        except Exception as e:
            print(f"✗ Build failed: {e}")
            return False
    
    def post_process_executable(self):
        """Post-process the built executable"""
        if self.current_os == "linux":
            # Make executable on Linux
            exe_path = self.dist_dir / self.executable_names["linux"]
            if exe_path.exists():
                exe_path.chmod(0o755)
                print(f"✓ Made executable file executable: {exe_path}")
        
        elif self.current_os == "darwin":
            # Handle macOS app bundle
            app_path = self.dist_dir / f"{self.app_name}.app"
            exe_path = self.dist_dir / self.executable_names["darwin"]
            
            if app_path.exists():
                print(f"✓ Created macOS app bundle: {app_path}")
                
                # Make the executable inside the bundle executable
                exe_in_bundle = app_path / "Contents" / "MacOS" / self.app_name
                if exe_in_bundle.exists():
                    exe_in_bundle.chmod(0o755)
            
            elif exe_path.exists():
                exe_path.chmod(0o755)
                print(f"✓ Made executable: {exe_path}")
        
        elif self.current_os == "windows":
            exe_path = self.dist_dir / self.executable_names["windows"]
            if exe_path.exists():
                print(f"✓ Created Windows executable: {exe_path}")
    
    def cleanup_build_artifacts(self):
        """Clean up build artifacts after successful build"""
        print("Cleaning up build artifacts...")
        
        # Remove build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"✓ Removed build directory: {self.build_dir}")
        
        # Remove spec file
        spec_files = list(self.project_dir.glob("*.spec"))
        for spec_file in spec_files:
            spec_file.unlink()
            print(f"✓ Removed spec file: {spec_file}")
        
        print("✓ Build artifacts cleaned up!")
    
    def create_launcher_script(self):
        """Create a launcher script that mimics 'python AutoBrightSpace.py run'"""
        if self.current_os == "windows":
            launcher_content = f'''@echo off
REM AutoBrightspace Quick Launcher
REM This script runs the same functionality as 'python AutoBrightSpace.py run'

cd /d "%~dp0"
"{self.executable_names["windows"]}" run
if errorlevel 1 (
    echo.
    echo Error: AutoBrightspace failed to run
    pause
)
'''
            launcher_path = self.dist_dir / "AutoBrightspace_QuickLogin.bat"
            
        elif self.current_os == "darwin":
            launcher_content = f'''#!/bin/bash
# AutoBrightspace Quick Launcher
# This script runs the same functionality as 'python AutoBrightSpace.py run'

DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$DIR"

if [ -d "{self.app_name}.app" ]; then
    # Run the app bundle with 'run' argument
    open -a "./{self.app_name}.app" --args run
else
    # Run the executable directly
    ./{self.executable_names["darwin"]} run
fi
'''
            launcher_path = self.dist_dir / "AutoBrightspace_QuickLogin.sh"
            
        else:  # Linux
            launcher_content = f'''#!/bin/bash
# AutoBrightspace Quick Launcher  
# This script runs the same functionality as 'python AutoBrightSpace.py run'

DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
cd "$DIR"

./{self.executable_names["linux"]} run

# If running in desktop environment, keep terminal open on error
if [ $? -ne 0 ] && [ -n "$DISPLAY" ]; then
    echo "Press Enter to continue..."
    read
fi
'''
            launcher_path = self.dist_dir / "AutoBrightspace_QuickLogin.sh"
        
        try:
            launcher_path.write_text(launcher_content)
            if self.current_os != "windows":
                launcher_path.chmod(0o755)
            
            print(f"✓ Created launcher script: {launcher_path}")
            return launcher_path
            
        except Exception as e:
            print(f"⚠ Could not create launcher script: {e}")
            return None
    
    def get_build_info(self):
        """Get information about the build"""
        exe_name = self.executable_names[self.current_os]
        
        if self.current_os == "darwin":
            # Check for app bundle first
            app_path = self.dist_dir / f"{self.app_name}.app"
            exe_path = self.dist_dir / exe_name
            
            if app_path.exists():
                size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
                return {
                    "path": app_path,
                    "size": size,
                    "type": "macOS App Bundle"
                }
            elif exe_path.exists():
                return {
                    "path": exe_path,
                    "size": exe_path.stat().st_size,
                    "type": "macOS Executable"
                }
        else:
            exe_path = self.dist_dir / exe_name
            if exe_path.exists():
                return {
                    "path": exe_path,
                    "size": exe_path.stat().st_size,
                    "type": f"{self.current_os.title()} Executable"
                }
        
        return None
    
    def print_build_summary(self):
        """Print a summary of the build process"""
        print("\n" + "="*50)
        print("BUILD SUMMARY")
        print("="*50)
        
        build_info = self.get_build_info()
        if build_info:
            size_mb = build_info["size"] / (1024 * 1024)
            print(f"✓ Built: {build_info['path']}")
            print(f"✓ Type: {build_info['type']}")
            print(f"✓ Size: {size_mb:.1f} MB")
            
            # Check for launcher
            launcher_scripts = list(self.dist_dir.glob("*QuickLogin*"))
            if launcher_scripts:
                print(f"✓ Launcher: {launcher_scripts[0].name}")
            
            print("\nUsage:")
            if self.current_os == "darwin" and (self.dist_dir / f"{self.app_name}.app").exists():
                print(f"• Double-click: {self.app_name}.app")
                print(f"• GUI mode: open {self.app_name}.app")
                print(f"• CLI mode: {self.app_name}.app/Contents/MacOS/{self.app_name} run")
                print(f"• Quick login: Double-click AutoBrightspace_QuickLogin.sh")
            else:
                exe_name = build_info["path"].name
                print(f"• Double-click: {exe_name}")
                print(f"• GUI mode: ./{exe_name}")
                print(f"• CLI mode: ./{exe_name} run")
                print(f"• Configure: ./{exe_name} config")
                launcher_name = "AutoBrightspace_QuickLogin.sh" if self.current_os != "windows" else "AutoBrightspace_QuickLogin.bat"
                print(f"• Quick login: {launcher_name}")
        else:
            print("✗ No executable found in dist/ directory")
        
        print("="*50)

def main():
    """Main function for the build script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build AutoBrightspace executable")
    parser.add_argument("--source", default="AutoBrightSpace.py", 
                       help="Source Python file (default: AutoBrightSpace.py)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build directories before building")
    parser.add_argument("--create-icons", action="store_true",
                       help="Force creation of default icons")
    
    args = parser.parse_args()
    
    # Initialize builder
    builder = AutoBrightspaceBuildTool(args.source)
    
    print(f"AutoBrightspace Build Tool")
    print(f"Platform: {builder.current_os}")
    print(f"Source: {builder.source_file}")
    print("-" * 40)
    
    # Create icons if requested
    if args.create_icons:
        builder.create_missing_icons()
        return
    
    # Clean if requested
    if args.clean:
        builder.clean_build_dirs()
        return
    
    # Build the executable
    if builder.build_executable():
        # Create launcher script
        builder.create_launcher_script()
        
        # Print summary
        builder.print_build_summary()
        
        print(f"\n✓ Build completed successfully!")
        print(f"Files are in: {builder.dist_dir}")
    else:
        print("\n✗ Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
