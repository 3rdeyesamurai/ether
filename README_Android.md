# UHFF Visualization Android Build Guide

This guide explains how to build the UHFF (Universal Harmonic Field Framework) Visualization app for Android using WSL (Windows Subsystem for Linux) and Buildozer.

## Features Added for Android

- **Touch Controls**: Full touch event support for Android devices
- **Virtual Buttons**: On-screen buttons for scene switching, mode toggles, and settings
- **Responsive UI**: Buttons and text scale with screen size
- **Fullscreen Mode**: Optimized for mobile display
- **Multi-orientation Support**: Works in both landscape and portrait modes

## Google Colab Build Troubleshooting

If you encounter "❌ Buildozer: Not found or error" in Google Colab:

### Quick Fixes:

1. **Restart Runtime**: Runtime > Restart runtime (not just session), then rerun script from beginning
2. **Manual Buildozer Install** (if auto-install fails):
   ```python
   !pip uninstall -y buildozer
   !pip install buildozer cython virtualenv pexpect --no-cache-dir
   !source ~/.bashrc && export PATH=$PATH:~/.local/bin
   ```

### Alternative: Use WSL Build Method

WSL has more reliable Android building. Switch to the WSL method below if Colab fails.

---

## Prerequisites (WSL Method)

1. **Windows with WSL2 installed**
2. **Ubuntu or similar Linux distribution in WSL**
3. **Sufficient disk space** (initial build requires ~2-3GB)

## Setup Instructions

### 1. Copy Project to WSL

```bash
# From Windows, copy the project to WSL
cp -r /mnt/c/Users/Kobyd/OneDrive/Documents/GitHub/ether ~/uhff-app
cd ~/uhff-app
```

### 2. Run Setup Script

```bash
# Make setup script executable and run it
chmod +x setup_wsl_android.sh
./setup_wsl_android.sh
```

This script will:
- Install Python, Java, and build tools
- Download and configure Android SDK
- Install Buildozer and dependencies
- Accept Android SDK licenses

### 3. Build the APK

```bash
# Make build script executable
chmod +x build_android.sh

# Build debug APK (first build takes 20-30 minutes)
./build_android.sh

# For clean build (removes previous build cache)
./build_android.sh clean
```

### 4. Install on Android Device

#### Method 1: ADB Install
```bash
# Connect Android device with USB debugging enabled
adb install bin/uhffvis-*-debug.apk
```

#### Method 2: Manual Install
1. Copy the APK from `bin/` directory to your Android device
2. Enable "Install from Unknown Sources" in Android settings
3. Tap the APK file to install

## Android Controls

### Touch Buttons (Bottom of Screen)
- **< Prev / Next >**: Switch between visualization scenes
- **Edit**: Toggle parameter edit mode
- **Auto**: Toggle auto-rotation
- **Zoom**: Toggle zoom level

### Second Row Buttons
- **Save**: Save current scene parameters as preset
- **Load**: Load most recent preset for current scene
- **Presets**: Browse saved presets
- **Help**: Show/hide help overlay

### Touch Gestures
- **Single Tap**: Activate buttons or interact with sliders
- **Drag**: Adjust parameter sliders in edit mode

## Troubleshooting

### Build Issues

1. **"Command not found" errors**:
   ```bash
   source ~/.bashrc
   export PATH=$PATH:$HOME/.local/bin
   ```

2. **Android SDK license issues**:
   ```bash
   yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses
   ```

3. **NDK download fails**:
   ```bash
   buildozer android clean
   # Edit buildozer.spec, change android.ndk version if needed
   ```

4. **Python/Cython compilation errors**:
   ```bash
   pip3 install --upgrade cython
   buildozer android clean
   ```

### Runtime Issues

1. **App crashes on startup**: Check if all dependencies are properly included in `buildozer.spec`

2. **Touch not working**: Ensure the device supports multi-touch and the app has proper permissions

3. **Performance issues**: The app is computationally intensive; try reducing visualization complexity

## Configuration

### Buildozer.spec Key Settings

- `requirements`: pygame, numpy, python3
- `orientation`: landscape, portrait
- `android.api`: 33 (latest)
- `android.minapi`: 21 (supports most devices)
- `p4a.bootstrap`: sdl2 (required for pygame)

### Customization

- Modify `get_button_layout()` in `main.py` to change button positions
- Adjust `is_mobile_device()` detection logic if needed
- Change screen resolution handling in `init_pygame()`

## Performance Notes

- First APK build downloads ~2GB of Android NDK and dependencies
- Subsequent builds are much faster (2-5 minutes)
- APK size is approximately 15-20MB
- App works best on devices with 2GB+ RAM

## File Structure

```
ether/
├── main.py                    # Main application with touch support
├── uhff_visualization.py      # Android entry point
├── buildozer.spec            # Android build configuration
├── setup_wsl_android.sh      # WSL setup script
├── build_android.sh          # APK build script
├── presets/                  # Saved visualization presets
└── bin/                      # Generated APK files (after build)
```

## Support

For build issues, check:
1. WSL and Ubuntu are properly installed and updated
2. All dependencies from setup script are installed
3. Android SDK licenses are accepted
4. Sufficient disk space available

The app has been tested with Android 7.0+ (API 21+) devices.
