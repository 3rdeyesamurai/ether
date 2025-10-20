#!/bin/bash
# WSL Android Build Setup Script for UHFF Visualization App

echo "Setting up Android build environment in WSL..."

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3 python3-pip python3-venv git openjdk-17-jdk \
    build-essential cmake ninja-build ccache libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev \
    libavformat-dev libavcodec-dev zlib1g-dev

# Install Android SDK command line tools
cd ~
mkdir -p android-sdk/cmdline-tools
cd android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-10406996_latest.zip
unzip commandlinetools-linux-10406996_latest.zip
mv cmdline-tools latest
rm commandlinetools-linux-10406996_latest.zip

# Set environment variables
echo 'export ANDROID_HOME=$HOME/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc

# Accept Android SDK licenses
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses

# Install required Android SDK components
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

# Install Buildozer
pip3 install --user buildozer

# Install Cython (required for some Android builds)
pip3 install --user cython

echo "Android build environment setup complete!"
echo "To build your APK:"
echo "1. Copy your project files to WSL"
echo "2. Navigate to your project directory"
echo "3. Run: buildozer android debug"
echo ""
echo "Note: First build will take a long time as it downloads Android NDK and other dependencies."