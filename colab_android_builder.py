#!/usr/bin/env python3
"""
UHFF Visualization - Android APK Builder for Google Colab

🚨 DO NOT RUN THIS FILE DIRECTLY! 🚨

This file contains instructions and code snippets for building Android APKs in Google Colab.
It is NOT a standalone Python script and will crash if run directly.

INSTRUCTIONS:
1. Open a new Google Colab notebook at: https://colab.research.google.com
2. Copy and paste each section between the === markers into separate Colab cells
3. Run the cells in order

For Windows/WSL users: Use build_android.sh and setup_wsl_android.sh scripts instead.

This Python file serves only as documentation and reference.
"""

def show_warning():
    print("🚨 WARNING: DO NOT RUN THIS FILE DIRECTLY!")
    print("")
    print("This file contains code snippets and instructions for Google Colab.")
    print("Running it directly will cause a kernel crash.")
    print("")
    print("Please follow these steps instead:")
    print("")
    print("1. WSL BUILD (Recommended for Windows users):")
    print("   - Run setup_wsl_android.sh")
    print("   - Run build_android.sh")
    print("")
    print("2. COLAB BUILD:")
    print("   - Open https://colab.research.google.com")
    print("   - Copy sections from this file into separate notebook cells")
    print("")
    print("See README_Android.md for detailed instructions.")

if __name__ == "__main__":
    show_warning()
    exit(1)

# =============================================================================
# COLAB BUILD PROCESS BELOW - COPY TO COLAB CELLS
# =============================================================================

"""
The sections below are the actual Colab commands.
To use them, copy each section into a separate Colab cell and run in order.

SECTION 1: Setup Environment - Copy this entire section to the first Colab cell
"""
print("🚀 Setting up Android build environment in Google Colab...")

# Install system dependencies - CRITICAL: These must be uncommented!
!apt-get update -qq
!apt-get install -y -qq openjdk-17-jdk wget unzip git build-essential

# Install additional build dependencies for Android development
!apt-get install -y -qq autoconf automake libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5
!apt-get install -y -qq cmake ninja-build ccache
!apt-get install -y -qq python3-pip python3-setuptools python3-wheel python3-dev

# Install Python dependencies with specific versions that work well together
print("📦 Installing buildozer and dependencies...")
!pip install --upgrade pip setuptools wheel
!pip install cython==0.29.36
!pip install buildozer==1.5.0
!pip install virtualenv pexpect sh colorama appdirs jinja2

# Verify buildozer installation
import sys
import os
from pathlib import Path
import shutil

# Set up PATH properly
pip_user_bin = Path.home() / ".local" / "bin"
if pip_user_bin.exists():
    os.environ['PATH'] = f"{pip_user_bin}:{os.environ['PATH']}"

# Add system bin directories
for bin_dir in ["/usr/local/bin", "/usr/bin", "/bin"]:
    if bin_dir not in os.environ['PATH']:
        os.environ['PATH'] = f"{bin_dir}:{os.environ['PATH']}"

# Verify buildozer is accessible
buildozer_path = shutil.which('buildozer')
if buildozer_path:
    print(f"✅ Buildozer found at: {buildozer_path}")
    # Test buildozer
    try:
        import subprocess
        result = subprocess.run(['buildozer', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Buildozer version: {result.stdout.strip()}")
        else:
            print(f"⚠️ Buildozer test failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Buildozer test error: {e}")
else:
    print("❌ Buildozer not found in PATH")

print("✅ System dependencies installed")

# =============================================================================
# STEP 2: Download and Setup Android SDK - Copy this section to the second Colab cell
# =============================================================================

import os
import zipfile
from pathlib import Path

# Create Android SDK directory
android_home = Path.home() / "android-sdk"
android_home.mkdir(exist_ok=True)

print("📥 Setting up Android SDK...")

# Download Android command line tools (updated to latest version)
cmdtools_url = "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
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
else:
    print("✅ Android SDK command line tools already installed")

# Set environment variables
os.environ['ANDROID_HOME'] = str(android_home)
os.environ['ANDROID_SDK_ROOT'] = str(android_home)  # Alternative name for some tools
os.environ['PATH'] = f"{android_home}/cmdline-tools/latest/bin:{android_home}/platform-tools:{os.environ['PATH']}"

# Fix permissions on SDK tools (common issue after extraction)
print("🔧 Fixing Android SDK permissions...")
!chmod +x {android_home}/cmdline-tools/latest/bin/* || true

# Accept licenses and install SDK components
if not (android_home / "platform-tools").exists():
    print("📦 Installing Android SDK components...")
    print("⏳ This may take a few minutes...")
    
    # Accept all licenses non-interactively
    !yes | {android_home}/cmdline-tools/latest/bin/sdkmanager --licenses
    
    # Install required SDK components
    !{android_home}/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"
    
    # Install NDK (required for buildozer)
    !{android_home}/cmdline-tools/latest/bin/sdkmanager "ndk;25.2.9519653"
    
    print("✅ Android SDK components installed")
else:
    print("✅ Android SDK components already installed")

# Verify installation
if (android_home / "platform-tools").exists():
    print("✅ Android SDK setup complete!")
    print(f"📍 SDK Location: {android_home}")
    print(f"📍 Platform Tools: {android_home}/platform-tools")
else:
    print("❌ Android SDK setup failed!")

# Show what we have
print("\n📋 Installed SDK components:")
!{android_home}/cmdline-tools/latest/bin/sdkmanager --list_installed | head -20

# =============================================================================
# STEP 3: Upload Project Files - Copy this section to the third Colab cell
# =============================================================================

print("📁 Setting up project files...")

# Option 1: Clone directly from your GitHub repository (RECOMMENDED)
print("🔽 Cloning project from GitHub...")
!git clone https://github.com/3rdeyesamurai/ether.git uhff-project

# Option 2: Manual upload (alternative method)
# Uncomment the lines below if you prefer to upload files manually:
"""
from google.colab import files
import zipfile
import shutil

def upload_project_files():
    print("📤 Upload your project as a ZIP file:")
    uploaded = files.upload()
    
    # Extract the uploaded ZIP
    for filename in uploaded.keys():
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall('uhff-project')
            os.remove(filename)
            print(f"✅ Extracted {filename}")
            break
    return True

# Uncomment to use manual upload:
# upload_project_files()
"""

# Verify project files
project_dir = Path("uhff-project")
if project_dir.exists():
    print(f"✅ Project directory created: {project_dir}")
    print("📋 Project files:")
    for item in project_dir.iterdir():
        if item.is_file():
            size_kb = item.stat().st_size / 1024
            print(f"  - {item.name} ({size_kb:.1f} KB)")
else:
    print("❌ Project directory not found!")
    print("Please check if the clone/upload was successful.")

# =============================================================================
# STEP 4: Configure Project for Android Build - Copy this section to the fourth Colab cell
# =============================================================================

import os
import shutil
from pathlib import Path

project_dir = Path("uhff-project")

print("🔧 Configuring project for Android build...")

# Create optimized buildozer.spec for Colab environment
buildozer_spec_content = '''[app]
title = UHFF Visualization App
package.name = uhffvis
package.domain = com.uhff
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = presets/*.json
version = 1.0

# Use specific working versions of requirements
requirements = python3,pygame,numpy,setuptools,six

# Entry point
source.main = main.py
orientation = landscape,portrait

[buildozer]
log_level = 2

# Android specific - optimized for Colab
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25.2.9519653
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True

# Use SDL2 bootstrap for pygame
p4a.bootstrap = sdl2

# Force clean builds to avoid cache issues in Colab
android.gradle_dependencies = 

# Optimize for Colab environment
android.gradle_repositories = 
android.enable_androidx = False

# Python for Android specific
p4a.branch = develop
p4a.bootstrap = sdl2
'''

# Write the optimized buildozer.spec
spec_path = project_dir / "buildozer.spec"
with open(spec_path, 'w') as f:
    f.write(buildozer_spec_content)
print(f"✅ Created optimized buildozer.spec")

# Verify project structure
if project_dir.exists():
    print(f"\n📁 Project structure:")
    for item in sorted(project_dir.iterdir()):
        if item.is_file():
            size_kb = item.stat().st_size / 1024
            print(f"  📄 {item.name} ({size_kb:.1f} KB)")
        elif item.is_dir():
            file_count = len(list(item.glob("*")))
            print(f"  📁 {item.name}/ ({file_count} files)")

# Check if we have the essential files
essential_files = ['main.py', 'uhff_visualization.py', 'buildozer.spec']
missing_files = []
for file in essential_files:
    if not (project_dir / file).exists():
        missing_files.append(file)

if missing_files:
    print(f"\n⚠️ Missing files: {missing_files}")
    print("The build may fail without these files.")
else:
    print(f"\n✅ All essential files present!")
    print("Ready for Android build!")

print(f"\n📍 Project directory: {project_dir.absolute()}")

# =============================================================================
# STEP 5: Build APK - Copy this section to the fifth Colab cell
# =============================================================================

import os
import subprocess
import shutil
from pathlib import Path

def build_apk():
    """Build the Android APK with enhanced error handling"""
    project_dir = Path("uhff-project")
    
    if not project_dir.exists():
        print("❌ Project directory not found!")
        return False
    
    # Change to project directory
    os.chdir(project_dir)
    print(f"� Working in: {project_dir.absolute()}")
    
    # Install additional build tools if needed
    print("🛠️ Ensuring build dependencies are available...")
    !apt-get install -qq libtool-bin automake pkg-config libffi-dev
    
    # Clean any previous builds
    print("🧹 Cleaning previous builds...")
    if Path(".buildozer").exists():
        shutil.rmtree(".buildozer")
        print("✅ Cleaned .buildozer directory")
    
    if Path("bin").exists():
        shutil.rmtree("bin")
        print("✅ Cleaned bin directory")
    
    # Verify buildozer is working
    try:
        result = subprocess.run(['buildozer', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Buildozer not working properly!")
            return False
        print(f"✅ Buildozer version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Buildozer check failed: {e}")
        return False
    
    # Start the build process
    print("\n🏗️ Starting APK build process...")
    print("⏳ This will take 15-30 minutes for the first build...")
    print("📊 Progress will be shown below:")
    
    try:
        # Use subprocess with real-time output
        process = subprocess.Popen(
            ['buildozer', 'android', 'debug', '-v'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ APK build completed successfully!")
            
            # List generated files
            bin_dir = Path("bin")
            if bin_dir.exists():
                apk_files = list(bin_dir.glob("*.apk"))
                if apk_files:
                    print(f"\n📱 Generated APK files:")
                    for apk in apk_files:
                        size_mb = apk.stat().st_size / 1024 / 1024
                        print(f"  - {apk.name} ({size_mb:.1f} MB)")
                    return True
                else:
                    print("❌ No APK files found in bin directory")
                    return False
            else:
                print("❌ Bin directory not found")
                return False
        else:
            print(f"\n❌ Build failed with return code {process.returncode}")
            print("Check the output above for error details.")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 45 minutes")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

# Run the build
success = build_apk()
if success:
    print("\n🎉 BUILD SUCCESSFUL!")
    print("Your APK is ready for download in the next step.")
else:
    print("\n💥 BUILD FAILED!")
    print("Please check the error messages above and try again.")

# =============================================================================
# STEP 6: Download APK - Copy this section to the sixth Colab cell
# =============================================================================

from google.colab import files
from pathlib import Path

def download_apk():
    """Download the built APK file"""
    project_dir = Path("uhff-project")
    bin_dir = project_dir / "bin"
    
    if not bin_dir.exists():
        print("❌ No build output found!")
        print("Make sure the build completed successfully.")
        return
    
    apk_files = list(bin_dir.glob("*.apk"))
    if not apk_files:
        print("❌ No APK files found to download!")
        return
    
    print("📥 Downloading APK files...")
    for apk_file in apk_files:
        size_mb = apk_file.stat().st_size / 1024 / 1024
        print(f"📱 Downloading {apk_file.name} ({size_mb:.1f} MB)...")
        files.download(str(apk_file))
        print(f"✅ Downloaded {apk_file.name}")
    
    print("\n🎉 Download complete!")
    print("You can now install the APK on your Android device.")

# Download the APK
download_apk()

# =============================================================================
# STEP 7: Utility Functions - Copy this section to the seventh Colab cell
# =============================================================================

import os
import shutil
from pathlib import Path

# Define project directory
project_dir = Path("uhff-project")

def show_project_files():
    """Show uploaded project files"""
    if project_dir.exists():
        print(f"📁 Files in {project_dir}:")
        total_size = 0
        for item in project_dir.iterdir():
            if item.is_file():
                size_mb = item.stat().st_size / 1024 / 1024
                total_size += size_mb
                print(f"  📄 {item.name} ({size_mb:.2f} MB)")
            elif item.is_dir() and item.name != '.git':
                file_count = len(list(item.glob("*")))
                print(f"  📁 {item.name}/ ({file_count} files)")
        print(f"\n📊 Total project size: {total_size:.2f} MB")
    else:
        print("❌ Project directory not found")

def clean_build():
    """Clean previous build artifacts"""
    if not project_dir.exists():
        print("❌ Project directory not found")
        return
    
    os.chdir(project_dir)
    
    # Clean buildozer cache
    if Path(".buildozer").exists():
        shutil.rmtree(".buildozer")
        print("✅ Cleaned .buildozer directory")
    
    # Clean bin directory
    if Path("bin").exists():
        shutil.rmtree("bin")
        print("✅ Cleaned bin directory")
    
    print("✅ Build cache cleaned - ready for fresh build")

def check_build_status():
    """Check the status of the build environment"""
    print("📊 Build Environment Status:")
    
    # Check Android SDK
    android_home = Path.home() / "android-sdk"
    sdk_status = "✅ Installed" if (android_home / "platform-tools").exists() else "❌ Missing"
    print(f"  - Android SDK: {sdk_status}")
    
    # Check project
    project_status = "✅ Ready" if project_dir.exists() else "❌ Missing"
    print(f"  - Project directory: {project_status}")
    
    # Check buildozer
    buildozer_path = shutil.which('buildozer')
    buildozer_status = "✅ Available" if buildozer_path else "❌ Missing"
    print(f"  - Buildozer: {buildozer_status}")
    
    # Check essential files
    if project_dir.exists():
        essential_files = ['main.py', 'buildozer.spec']
        missing = [f for f in essential_files if not (project_dir / f).exists()]
        if missing:
            print(f"  - Essential files: ❌ Missing {missing}")
        else:
            print(f"  - Essential files: ✅ All present")
    
    # Overall status
    all_good = (
        (android_home / "platform-tools").exists() and
        project_dir.exists() and
        buildozer_path and
        (project_dir / "main.py").exists() and
        (project_dir / "buildozer.spec").exists()
    )
    
    print(f"\n🎯 Overall Status: {'✅ Ready to build!' if all_good else '❌ Setup incomplete'}")
    
    return all_good

# Run status check
print("🔍 Checking build environment...")
check_build_status()

print("\n� Available utility functions:")
print("  - show_project_files(): List all project files")
print("  - clean_build(): Clean build cache")
print("  - check_build_status(): Check environment status")

print("\n💡 Quick Start Guide:")
print("1. Run each cell in order (1-6)")
print("2. Wait for Step 5 (build) to complete (~20-30 minutes)")
print("3. Download your APK in Step 6")
print("4. Install on Android device and enjoy!")
