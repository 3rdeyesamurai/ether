# 🌌 UHFF Visualization App

**Universal Harmonic Field Framework (UHFF) - Interactive Mathematical Visualization Platform**

A powerful cross-platform visualization tool for exploring mathematical concepts through interactive 3D animations, featuring advanced harmonic field equations, geometric transformations, and quantum-inspired visualizations.

![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20Android-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### 🎯 **Interactive Visualizations**
- **11 Mathematical Scenes**: From Fibonacci spirals to quantum phase alignments
- **Real-time Parameter Editing**: Adjust mathematical parameters with instant visual feedback
- **3D Rotation & Projection**: Dynamic camera controls with quaternion-based rotations
- **Advanced Rendering**: Vectorized NumPy operations for high-performance graphics

### 📱 **Multi-Platform Support**
- **Desktop**: Full keyboard and mouse controls
- **Android**: Touch-optimized interface with virtual buttons
- **Responsive UI**: Adaptive scaling for different screen sizes and resolutions

### ⚡ **Performance Optimizations**
- **Vectorized Rendering**: ~10x speedup with NumPy array operations
- **Adaptive Frame Rate**: 60 FPS desktop, 30 FPS mobile
- **Mobile Optimizations**: Efficient touch handling and battery-conscious rendering

### 🎮 **User Interface**
- **Dual Control Modes**: Keyboard shortcuts + touch-friendly virtual buttons
- **Preset System**: Save, load, and manage visualization configurations
- **Live Parameter Adjustment**: Sliders and numeric input for real-time tweaking
- **Help System**: Built-in controls reference and scene descriptions

## 🧮 Mathematical Scenes

| Scene | Description | Key Parameters |
|-------|-------------|----------------|
| **Fibonacci Torus Knots** | Parametric knot topology with golden ratio scaling | `p`, `q`, `R`, `r` |
| **Force Gradient Flow** | Vector field visualization with directional arrows | Dynamic field calculation |
| **Golden Ratio Overtones** | Fibonacci spiral with harmonic scaling | `phi`, `num_points` |
| **Gravity Harmonic Pressure** | 3D density fields from wave superposition | `num_points` |
| **Mass Phase-Locked Density** | Standing wave patterns with time evolution | `amp`, `freq`, `t` |
| **Quantum Phase Alignment** | Dual-wave interference patterns | `phase_diff` |
| **Quaternion Rotation** | 3D object transformation demo | `angle`, `axis` |
| **Spacetime Emergent Geometry** | Converging wave interactions | Wave convergence |
| **Golden Torus Spiral** | Exponentially scaled toroidal helix | `turns`, `R`, `r` |
| **Harmonic Lattice** | 2D grid with summed harmonic modes | `nx`, `ny`, `modes` |
| **Harmonic Superposition** | Multi-frequency wave interference | `num_waves`, `amplitudes` |

## 🚀 Quick Start

### Desktop Installation

```bash
# Clone the repository
git clone https://github.com/3rdeyesamurai/ether.git
cd ether

# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install pygame numpy

# Run the application
python main.py
```

### Android Build

Choose your preferred build environment:

#### Option 1: Google Colab (Recommended)
```python
# Upload UHFF_Android_Builder_Fixed.ipynb to Google Colab
# Follow the step-by-step notebook instructions
# Download the generated APK
```

#### Option 2: WSL/Ubuntu
```bash
# Copy project to WSL
cp -r /path/to/ether ~/uhff-app
cd ~/uhff-app

# Run setup script
chmod +x setup_wsl_android.sh
./setup_wsl_android.sh

# Build APK
chmod +x build_android.sh
./build_android.sh
```

## 🎮 Controls

### Desktop Controls
| Key | Action | Description |
|-----|--------|-------------|
| `←` / `→` | Scene Navigation | Switch between visualization scenes |
| `E` | Edit Mode | Toggle parameter editing |
| `Tab` | Parameter Cycle | Select next editable parameter |
| `↑` / `↓` | Adjust Parameter | Modify selected parameter value |
| `A` | Auto-Rotate | Toggle automatic 3D rotation |
| `Z` | Zoom | Toggle between 1x and 2x zoom levels |
| `S` | Save Preset | Save current scene parameters |
| `L` | Load Preset | Load most recent preset |
| `P` | Preset Browser | Open preset management interface |
| `H` | Help | Show/hide control reference |

### Mobile/Touch Controls
- **Virtual Buttons**: On-screen controls for all major functions
- **Touch Sliders**: Drag to adjust parameters in edit mode
- **Responsive Layout**: Buttons scale with screen size
- **Visual Feedback**: Active states highlighted

## 🏗️ Architecture

### Core Components

```python
# Main Application Loop
main()                          # Entry point and event handling

# 3D Mathematics
rotate_points()                 # 3D rotation matrices
project()                       # 3D to 2D projection with vectorization
coerce_points()                 # Data normalization for various input types

# Scene Generators
gen_torus_knot()               # Parametric knot generation
gen_fib_spiral()               # Golden ratio spirals
gen_harmonic_superposition()   # Wave interference patterns
# ... + 8 more mathematical generators

# Platform Adaptation
init_pygame()                  # Cross-platform graphics initialization
is_mobile_device()            # Platform detection
get_button_layout()           # Responsive UI positioning
handle_touch_input()          # Touch event processing
```

### Performance Features

#### Vectorized Rendering
```python
# Before: Python loop (slow)
for point in points:
    factor = screen_dist / (eye_z - z)
    px = WIDTH / 2 + x * factor * 100
    
# After: NumPy vectorization (10x faster)
factor = np.where(eye_z - z != 0, screen_dist / (eye_z - z), 1)
px = WIDTH / 2 + x * factor * 100
```

#### Adaptive Performance
```python
# Dynamic FPS based on platform
fps_target = 30 if is_mobile_device() else 60
clock.tick(fps_target)
```

## 📁 Project Structure

```
ether/
├── 📱 Core Application
│   ├── main.py                 # Main application with full touch support
│   ├── uhff_visualization.py   # Android entry point wrapper
│   └── presets/               # Saved visualization configurations
│
├── 🔧 Build System
│   ├── buildozer.spec          # Android build configuration
│   ├── setup_wsl_android.sh    # WSL environment setup
│   ├── build_android.sh        # APK build script
│   └── copy_to_wsl.ps1         # Windows->WSL transfer utility
│
├── ☁️ Cloud Building
│   ├── UHFF_Android_Builder_Fixed.ipynb    # Comprehensive Colab builder
│   ├── UHFF_Android_Builder.ipynb          # Original Colab builder  
│   └── colab_android_builder.py            # Python build script
│
└── 📚 Documentation
    ├── README.md               # This file
    ├── README_Android.md       # Android-specific build guide
    └── Google_Colab_Guide.md   # Cloud build instructions
```

## ⚙️ Technical Specifications

### Requirements
- **Python**: 3.11+ (3.12+ for latest features)
- **Core Dependencies**: pygame 2.1.3+, numpy 1.24.3+
- **Android**: API 21+ (Android 5.0+), 2GB+ RAM recommended
- **Desktop**: Windows 10+, Ubuntu 18.04+, macOS 10.14+

### Build Configuration
```toml
# buildozer.spec highlights
requirements = python3,pygame,numpy
android.archs = arm64-v8a        # Optimized for modern devices
android.api = 33                 # Latest Android target
android.minapi = 21             # Broad device compatibility
p4a.bootstrap = sdl2            # Required for pygame
orientation = landscape,portrait # Sensor-based rotation
fullscreen = 1                  # Immersive mobile experience
```

### Performance Metrics
- **Vectorized Projection**: ~10x rendering speedup
- **Memory Usage**: ~50MB base, scales with scene complexity
- **APK Size**: 15-20MB (includes pygame + numpy)
- **Build Time**: 20-30 minutes first build, 2-5 minutes subsequent

## 🔧 Development

### Adding New Scenes
```python
# 1. Create generator function
def gen_my_visualization(param1=1.0, param2=2.0):
    # Return Nx3 numpy array of 3D points
    return np.column_stack((x, y, z))

# 2. Add to scenes list
scenes.append({
    "name": "12. My Visualization",
    "gen": gen_my_visualization,
    "params": {"param1": 1.0, "param2": 2.0},
    "param_meta": {
        "param1": {"type": "float", "min": 0.1, "max": 10.0, "step": 0.1}
    }
})
```

### Building for Android
See detailed guides:
- **[Android Build Guide](README_Android.md)** - WSL/Ubuntu setup
- **[Google Colab Guide](Google_Colab_Guide.md)** - Cloud building

### Troubleshooting
Common issues and solutions:

**Build Fails**: Use single architecture (`android.archs = arm64-v8a`)
**Touch Not Working**: Check `handle_touch_input()` and button positioning
**Performance Issues**: Reduce `num_points` in scene parameters
**Import Errors**: Verify pygame/numpy versions match buildozer.spec

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-visualization`
3. **Add** your mathematical scene generator
4. **Test** on both desktop and mobile
5. **Submit** pull request with performance benchmarks

### Contribution Guidelines
- Follow NumPy vectorization patterns for performance
- Ensure mobile compatibility with touch events
- Add parameter metadata for UI sliders
- Include mathematical documentation for new scenes

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mathematical Foundations**: Based on harmonic field theory and quantum-inspired visualizations
- **Cross-Platform Support**: pygame and SDL2 communities
- **Android Integration**: Kivy project and python-for-android toolchain
- **Performance Optimization**: NumPy and scientific Python ecosystem

---

**Built with ❤️ for mathematical exploration and visual discovery**

*Explore the universe through mathematics - from Fibonacci spirals to quantum harmonics* 🌌