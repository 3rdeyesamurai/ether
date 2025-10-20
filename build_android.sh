#!/bin/bash
# Android Build Script for UHFF Visualization App

echo "Building UHFF Visualization APK..."

# Clean previous builds if needed
if [ "$1" = "clean" ]; then
    echo "Cleaning previous builds..."
    buildozer android clean
fi

# Build debug APK
echo "Starting Android debug build..."
buildozer android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful! APK created in bin/ directory"
    ls -la bin/*.apk
    echo ""
    echo "To install on device:"
    echo "1. Enable Developer Options and USB Debugging on your Android device"
    echo "2. Connect device via USB"
    echo "3. Run: adb install bin/uhffvis-*-debug.apk"
    echo ""
    echo "Or copy the APK to your device and install manually"
else
    echo "Build failed! Check the output above for errors."
    echo ""
    echo "Common issues:"
    echo "- Missing dependencies: run setup_wsl_android.sh first"
    echo "- Android SDK/NDK issues: check buildozer.spec configuration"
    echo "- Python package issues: verify requirements in buildozer.spec"
fi