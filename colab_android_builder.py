# UHFF Visualization - Android APK Builder for Google Colab
# This notebook builds your UHFF app into an Android APK using Google Colab

# =============================================================================
# STEP 1: Setup Environment
# =============================================================================

print("🚀 Setting up Android build environment in Google Colab...")
print("This process will take about 10-15 minutes for the first run.")

# Update system and install dependencies
!apt-get update -qq
!apt-get install -y -qq openjdk-17-jdk wget unzip git

# Install Python dependencies
!pip install buildozer cython

print("✅ Basic dependencies installed")

# =============================================================================
# STEP 2: Download and Setup Android SDK
# =============================================================================

import os
import zipfile
from pathlib import Path

# Create Android SDK directory
android_home = Path.home() / "android-sdk"
android_home.mkdir(exist_ok=True)

# Download Android command line tools
cmdtools_url = "https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip"
cmdtools_zip = "commandlinetools.zip"

if not (android_home / "cmdline-tools" / "latest").exists():
    print("📥 Downloading Android SDK command line tools...")
    !wget -q {cmdtools_url} -O {cmdtools_zip}
    
    # Extract command line tools
    with zipfile.ZipFile(cmdtools_zip, 'r') as zip_ref:
        zip_ref.extractall(android_home / "cmdline-tools")
    
    # Move to correct directory structure
    import shutil
    shutil.move(
        str(android_home / "cmdline-tools" / "cmdline-tools"),
        str(android_home / "cmdline-tools" / "latest")
    )
    os.remove(cmdtools_zip)
    print("✅ Android SDK command line tools installed")

# Set environment variables
os.environ['ANDROID_HOME'] = str(android_home)
os.environ['PATH'] = f"{android_home}/cmdline-tools/latest/bin:{android_home}/platform-tools:{os.environ['PATH']}"

# Accept licenses and install SDK components
if not (android_home / "platform-tools").exists():
    print("📦 Installing Android SDK components...")
    !yes | {android_home}/cmdline-tools/latest/bin/sdkmanager --licenses
    !{android_home}/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
    print("✅ Android SDK components installed")

# =============================================================================
# STEP 3: Upload Project Files
# =============================================================================

print("\n📁 Please upload your project files...")
print("You can either:")
print("1. Upload files manually using the Colab file browser")
print("2. Clone from GitHub")
print("3. Upload a ZIP file")

# Option 1: Manual file upload
from google.colab import files
import zipfile
import shutil

def upload_project_files():
    """Upload project files to Colab"""
    print("Choose an option:")
    print("1. Upload ZIP file of your project")
    print("2. Clone from GitHub repository")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        print("Please upload your project as a ZIP file:")
        uploaded = files.upload()
        
        # Extract the uploaded ZIP
        for filename in uploaded.keys():
            if filename.endswith('.zip'):
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall('uhff-project')
                os.remove(filename)
                print(f"✅ Extracted {filename}")
                break
    
    elif choice == "2":
        repo_url = input("Enter GitHub repository URL (https://github.com/...): ")
        !git clone {repo_url} uhff-project
        print("✅ Repository cloned")
    
    else:
        print("❌ Invalid choice")
        return False
    
    return True

# For direct use (if you want to clone your repo)
# Uncomment and modify the line below:
# !git clone https://github.com/3rdeyesamurai/ether.git uhff-project

# Or upload files manually
# upload_project_files()

print("\n📋 If uploading manually, please ensure these files are in 'uhff-project' directory:")
print("- main.py")
print("- uhff_visualization.py") 
print("- buildozer.spec")
print("- Any other Python files")

# =============================================================================
# STEP 4: Create Project Structure (if files uploaded manually)
# =============================================================================

# Create project directory if it doesn't exist
project_dir = Path("uhff-project")
project_dir.mkdir(exist_ok=True)

# If you uploaded files manually to the root, move them to project directory
def organize_files():
    """Move uploaded files to proper project structure"""
    files_to_move = ['main.py', 'uhff_visualization.py', 'buildozer.spec']
    for file in files_to_move:
        if Path(file).exists() and not (project_dir / file).exists():
            shutil.move(file, project_dir / file)
            print(f"✅ Moved {file} to project directory")

# =============================================================================
# STEP 5: Create/Update Project Files for Colab
# =============================================================================

# Create the main files if they don't exist (in case of manual setup)
main_py_content = '''
# Your main.py content would go here
# This is a placeholder - upload your actual main.py file
import pygame
import numpy as np

def main():
    print("UHFF Visualization - Android Build")
    print("Please upload your actual main.py file")

if __name__ == "__main__":
    main()
'''

uhff_py_content = '''#!/usr/bin/env python3
"""
UHFF Visualization Entry Point for Android
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from main import main
    
    if __name__ == "__main__":
        print("Starting UHFF Visualization for Android...")
        main()
        
except ImportError as e:
    print(f"Error importing main module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
'''

buildozer_spec_content = '''[app]
title = UHFF Visualization App
package.name = uhffvis
package.domain = com.uhff
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,pygame,numpy
orientation = landscape,portrait

[buildozer]
log_level = 2

# Android specific
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2
'''

# Write default files if they don't exist
def create_default_files():
    """Create default project files if they don't exist"""
    files_to_create = {
        'main.py': main_py_content,
        'uhff_visualization.py': uhff_py_content,
        'buildozer.spec': buildozer_spec_content
    }
    
    for filename, content in files_to_create.items():
        filepath = project_dir / filename
        if not filepath.exists():
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created default {filename}")

# =============================================================================
# STEP 6: Build APK
# =============================================================================

def build_apk():
    """Build the Android APK"""
    os.chdir(project_dir)
    
    print("🏗️ Starting APK build process...")
    print("This will take 15-30 minutes for the first build as it downloads dependencies.")
    
    # Initialize buildozer (downloads Android NDK, etc.)
    !buildozer android debug
    
    print("✅ APK build completed!")
    
    # List generated files
    bin_dir = Path("bin")
    if bin_dir.exists():
        apk_files = list(bin_dir.glob("*.apk"))
        if apk_files:
            print(f"\n📱 Generated APK files:")
            for apk in apk_files:
                print(f"  - {apk.name} ({apk.stat().st_size / 1024 / 1024:.1f} MB)")
        else:
            print("❌ No APK files found in bin directory")
    else:
        print("❌ Bin directory not found")

def download_apk():
    """Download the built APK file"""
    bin_dir = Path(project_dir / "bin")
    if bin_dir.exists():
        apk_files = list(bin_dir.glob("*.apk"))
        if apk_files:
            print("📥 Downloading APK file...")
            for apk_file in apk_files:
                files.download(str(apk_file))
                print(f"✅ Downloaded {apk_file.name}")
        else:
            print("❌ No APK files found to download")
    else:
        print("❌ No build output found")

# =============================================================================
# STEP 7: Main Execution
# =============================================================================

print("\n" + "="*60)
print("🎯 READY TO BUILD!")
print("="*60)
print("\nNext steps:")
print("1. Upload your project files (main.py, buildozer.spec, etc.)")
print("2. Run the build process")
print("3. Download the generated APK")
print("\nTo start building, run:")
print("build_apk()")
print("\nTo download the APK after building:")
print("download_apk()")

# Utility functions for user
def show_project_files():
    """Show uploaded project files"""
    if project_dir.exists():
        print(f"📁 Files in {project_dir}:")
        for item in project_dir.iterdir():
            if item.is_file():
                size_mb = item.stat().st_size / 1024 / 1024
                print(f"  - {item.name} ({size_mb:.2f} MB)")
    else:
        print("❌ Project directory not found")

def clean_build():
    """Clean previous build artifacts"""
    os.chdir(project_dir)
    !buildozer android clean
    print("✅ Build cache cleaned")

# Show current status
print(f"\n📊 Current status:")
print(f"  - Android SDK: {'✅ Installed' if (android_home / 'platform-tools').exists() else '❌ Missing'}")
print(f"  - Project directory: {'✅ Ready' if project_dir.exists() else '❌ Missing'}")
print(f"  - Buildozer: {'✅ Installed' if shutil.which('buildozer') else '❌ Missing'}")