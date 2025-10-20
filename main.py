import json
import numpy as np
from math import sin, cos, pi, sqrt
import os
from datetime import datetime
from typing import Optional

# Window setup
WIDTH, HEIGHT = 800, 600


# Make pygame optional so this module can be imported on platforms where
# pygame isn't available (for example during Android/Buildozer packaging).
try:
    import pygame as _pygame
except Exception:
    _pygame = None


def init_pygame(width=WIDTH, height=HEIGHT, title="UHFF Visualization App"):
    """Initialize pygame and return (screen, clock, font).

    This prevents side-effects at import time so the module can be imported
    without opening a window. Callers (or the module's main) should call
    this before entering any event/rendering loop.
    """
    if _pygame is None:
        raise RuntimeError("pygame is not available in this environment")
    
    _pygame.init()
    
    # Get available display info for mobile optimization
    try:
        info = _pygame.display.Info()
        if is_mobile_device():
            # Use native resolution on mobile devices
            width = info.current_w if info.current_w > 0 else width
            height = info.current_h if info.current_h > 0 else height
            # Update global width/height for mobile
            global WIDTH, HEIGHT
            WIDTH, HEIGHT = width, height
    except:
        # Fallback to default if display info fails
        pass
    
    # For Android, use fullscreen mode
    flags = _pygame.FULLSCREEN if is_mobile_device() else 0
    screen = _pygame.display.set_mode((width, height), flags)
    _pygame.display.set_caption(title)
    clock = _pygame.time.Clock()
    
    # Use larger font on mobile devices
    font_size = 32 if is_mobile_device() else 24
    font = _pygame.font.SysFont(None, font_size)
    
    return screen, clock, font

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 3D Projection and Rotation Functions
def rotate_points(points, angle_x, angle_y, angle_z):
    rx = np.array([[1, 0, 0], [0, cos(angle_x), -sin(angle_x)], [0, sin(angle_x), cos(angle_x)]])
    ry = np.array([[cos(angle_y), 0, sin(angle_y)], [0, 1, 0], [-sin(angle_y), 0, cos(angle_y)]])
    rz = np.array([[cos(angle_z), -sin(angle_z), 0], [sin(angle_z), cos(angle_z), 0], [0, 0, 1]])
    rot = rz @ ry @ rx
    return points @ rot.T


def coerce_points(points):
    """Coerce various generator return shapes into an Nx3 float numpy array.

    Accepts lists, (N,2), (N,3), (nx,ny,3) grids, and will flatten as needed.
    """
    if points is None:
        return np.empty((0, 3), dtype=float)
    arr = np.asarray(points)
    if arr.size == 0:
        return np.empty((0, 3), dtype=float)
    # If it's a 3D grid like (nx,ny,...) flatten to (N,dim)
    if arr.ndim > 2 and arr.shape[-1] in (2, 3):
        arr = arr.reshape(-1, arr.shape[-1])
    # If last dim is not 2 or 3 but array is 2D, try to infer
    if arr.ndim == 2 and arr.shape[1] not in (2, 3):
        # attempt to split evenly into 3 columns
        flat = arr.ravel()
        if flat.size % 3 == 0:
            arr = flat.reshape(-1, 3)
        elif flat.size % 2 == 0:
            arr = flat.reshape(-1, 2)
        else:
            # fallback: pad/truncate
            needed = ((flat.size + 2) // 3) * 3
            pad = np.zeros(needed - flat.size)
            arr = np.concatenate([flat, pad]).reshape(-1, 3)
    # Now ensure 2->3 conversion and float dtype
    if arr.ndim == 1:
        if arr.size == 3:
            arr = arr.reshape(1, 3)
        elif arr.size == 2:
            arr = np.hstack([arr.reshape(1, 2), np.zeros((1, 1))])
        else:
            vals = list(arr.ravel())
            while len(vals) < 3:
                vals.append(0.0)
            arr = np.array([vals[:3]], dtype=float)
    if arr.ndim == 2:
        if arr.shape[1] == 2:
            arr = np.hstack([arr, np.zeros((arr.shape[0], 1))])
        elif arr.shape[1] > 3:
            arr = arr[:, :3]
        elif arr.shape[1] < 3:
            pad = np.zeros((arr.shape[0], 3 - arr.shape[1]))
            arr = np.hstack([arr, pad])
    return arr.astype(float)

def project(points, eye_z=-5, screen_dist=4, zoom=1.0):
    """Project 3D points to 2D screen coordinates with a zoom factor.

    zoom > 1.0 makes objects appear smaller (zoomed out); zoom < 1.0 zooms in.
    """
    projected = []
    for point in points:
        try:
            x, y, z = point
        except Exception:
            continue
        factor = screen_dist / (eye_z - z) if (eye_z - z) != 0 else 1
        px = WIDTH / 2 + x * factor * 100 / zoom
        py = HEIGHT / 2 - y * factor * 100 / zoom
        projected.append((int(px), int(py)))
    return projected

# Concept Functions (return 3D points or data; params adjustable)
def gen_torus_knot(p=2, q=3, R=1, r=0.4, num_points=1000):
    t = np.linspace(0, 2 * pi, num_points)
    x = (R + r * np.cos(q * t)) * np.cos(p * t)
    y = (R + r * np.cos(q * t)) * np.sin(p * t)
    z = r * np.sin(q * t)
    return np.column_stack((x, y, z))

def gen_gradient_flow(num_arrows=20):
    # Scalar field: sin(kx + phi), gradient as arrows
    x, y = np.meshgrid(np.linspace(-2, 2, num_arrows), np.linspace(-2, 2, num_arrows))
    field = np.sin(2 * pi * x + pi / 4) + np.cos(2 * pi * y)
    dx = np.cos(2 * pi * x + pi / 4) * 2 * pi  # Partial deriv
    dy = -np.sin(2 * pi * y) * 2 * pi
    points = []
    for i in range(num_arrows):
        for j in range(num_arrows):
            start = [x[i,j], y[i,j], field[i,j] * 0.1]
            end = [x[i,j] + dx[i,j]*0.1, y[i,j] + dy[i,j]*0.1, start[2]]
            points.append(start)
            points.append(end)
    return coerce_points(points)

def gen_fib_spiral(num_points=200, phi=(1 + sqrt(5))/2):
    points = []
    for i in range(num_points):
        r = sqrt(i)
        theta = i * 2 * pi / phi**2
        x = r * cos(theta)
        y = r * sin(theta)
        points.append([x, y, 0])
    return np.array(points)

def gen_harmonic_pressure(num_points=20):
    # Density field from summed harmonics
    x, y, z = np.meshgrid(np.linspace(-1,1,num_points), np.linspace(-1,1,num_points), np.linspace(-1,1,num_points))
    density = np.sin(2*pi*x) + np.cos(2*pi*y) + np.sin(2*pi*z)  # Summed waves
    points = np.column_stack((x.ravel(), y.ravel(), density.ravel() * 0.5))  # z as pressure
    return coerce_points(points)

def gen_standing_wave(num_points=500, amp=1, freq=2, t=0):
    """Generate a standing wave curve.

    Args:
        num_points: number of spatial sample points.
        amp: amplitude multiplier.
        freq: spatial frequency (multiplies x).
        t: time parameter (seconds) used in the temporal cos factor; default
           0 produces the static snapshot. Use this to animate: cos(2*pi*t).
    Returns:
        Nx3 array of points suitable for rotation/projection (x, y, z).
    """
    x = np.linspace(-pi, pi, num_points)
    wave = amp * np.sin(freq * x) * np.cos(2 * pi * t)  # Standing wave (time-modulated)
    points = []
    for i in range(len(x)):
        points.append([x[i], wave[i], 0])
        points.append([x[i], 0, wave[i]])  # 3D extrusion
    return np.array(points)

def gen_phase_alignment(num_points=200, phase_diff=pi/2):
    x = np.linspace(0, 2*pi, num_points)
    wave1 = np.sin(x)
    wave2 = np.sin(x + phase_diff)
    # collapse was previously computed but unused; removed to avoid dead code
    points = np.column_stack((x, wave1, wave2))
    return points

def gen_quaternion_rotation(angle=0.0, axis=None):
    # Simple cube; accept optional angle and axis so callers can pass params
    cube = np.array([[-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, -0.5], [-0.5, 0.5, 0.5],
                     [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5]])
    if axis is None:
        return cube
    try:
        axis_arr = np.array(axis, dtype=float)
        if np.linalg.norm(axis_arr) == 0:
            return cube
        return apply_quat_rotation(cube, angle, axis_arr)
    except Exception:
        return cube

def quaternion_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2
    return np.array([w, x, y, z])

def apply_quat_rotation(points, angle, axis):
    axis = axis / np.linalg.norm(axis)
    q = np.array([cos(angle/2), *(sin(angle/2)*axis)])
    q_inv = np.array([q[0], -q[1], -q[2], -q[3]])
    rotated = []
    for p in points:
        qp = np.array([0, *p])
        rotated.append(quaternion_mult(quaternion_mult(q, qp), q_inv)[1:])
    return np.array(rotated)

def gen_converging_waves(num_points=200):
    # Converging harmonics forming geometry
    t = np.linspace(0, 2*pi, num_points)
    wave1 = np.sin(t)[:, np.newaxis] * np.array([1,0,0])
    wave2 = np.cos(t + pi/3)[:, np.newaxis] * np.array([0,1,0])
    converged = wave1 + wave2
    return converged

def gen_trefoil():
    return gen_torus_knot(2, 3, 1, 0.4)

def gen_interference(num_waves=3, num_points=20):
    x, y, z = np.meshgrid(np.linspace(-1,1,num_points), np.linspace(-1,1,num_points), np.linspace(-1,1,num_points))
    field = sum(np.sin(2*pi*(x + i*0.5)) + np.cos(2*pi*(y + i*0.3)) for i in range(num_waves))
    points = np.column_stack((x.ravel(), y.ravel(), field.ravel() * 0.2))
    return coerce_points(points)

def gen_harmonic_superposition(num_waves=5, num_points=400, x_min=-pi, x_max=pi, amplitudes=None, freqs=None, phases=None, t=0):
    num_waves = int(num_waves); num_points = int(num_points)
    """Sum multiple sinusoidal modes to visualize U(x,t).

    Returns Nx3 array where columns are (x, U(x,t), 0).
    """
    x = np.linspace(x_min, x_max, num_points)
    if amplitudes is None:
        amplitudes = [1.0/(i+1) for i in range(num_waves)]
    if freqs is None:
        freqs = [1.0*(i+1) for i in range(num_waves)]
    if phases is None:
        phases = [0.0 for _ in range(num_waves)]
    U = np.zeros_like(x)
    for i in range(num_waves):
        A = amplitudes[i % len(amplitudes)]
        k = freqs[i % len(freqs)]
        phi = phases[i % len(phases)]
        U += A * np.sin(k * x - 2*pi*k*t + phi)
    points = np.column_stack((x, U, np.zeros_like(x)))
    return points

def gen_golden_torus_spiral(num_points=1000, turns=5, R=1.0, r=0.2, phi=(1+sqrt(5))/2):
    """Create a toroidal spiral that scales radially by the golden ratio."""
    t = np.linspace(0, 2*pi*turns, num_points)
    scale = phi ** (t / (2*pi*turns))  # exponential scaling across turns
    x = (R + r * np.cos(3 * t)) * np.cos(2 * t) * scale
    y = (R + r * np.cos(3 * t)) * np.sin(2 * t) * scale
    z = r * np.sin(3 * t) * scale
    return np.column_stack((x, y, z))

def gen_harmonic_lattice(nx=32, ny=32, modes=3):
    """2D lattice with summed harmonics mapped to z-axis for visualization."""
    nx = int(nx); ny = int(ny); modes = int(modes)
    xs = np.linspace(-2, 2, nx)
    ys = np.linspace(-2, 2, ny)
    points = []
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            z = 0.0
            for m in range(1, modes+1):
                z += (1.0/m) * np.sin(m * (x + y))
            points.append([x, y, z * 0.5])
    return coerce_points(points)

# Scenes: list of dicts with name, gen_func, params
scenes = [
    {"name": "1. Fibonacci Torus Knots", "gen": gen_torus_knot, "params": {"p":2, "q":3, "R":1.0, "r":0.4},
     "param_meta": {
         "p": {"type": "int", "min": 1, "max": 50, "step": 1},
         "q": {"type": "int", "min": 1, "max": 50, "step": 1},
         "R": {"type": "float", "min": 0.1, "max": 10.0, "step": 0.1},
         "r": {"type": "float", "min": 0.01, "max": 5.0, "step": 0.01}
     }},
    {"name": "2. Force Gradient Flow", "gen": gen_gradient_flow, "params": {}},
    {"name": "3. Golden Ratio Overtone", "gen": gen_fib_spiral, "params": {"phi": (1+sqrt(5))/2}},
    {"name": "4. Gravity Harmonic Pressure", "gen": gen_harmonic_pressure, "params": {}},
    {"name": "5. Mass Phase-Locked Density", "gen": gen_standing_wave, "params": {"amp":1.0, "freq":2.0}},
    {"name": "6. Quantum Phase Alignment", "gen": gen_phase_alignment, "params": {"phase_diff": pi/2}},
    {"name": "7. Quaternion Rotation", "gen": gen_quaternion_rotation, "params": {"angle":0.0, "axis":np.array([1.0,1.0,1.0])}},
    {"name": "8. Spacetime Emergent Geom", "gen": gen_converging_waves, "params": {}},
    {"name": "9. Golden Torus Spiral", "gen": gen_golden_torus_spiral, "params": {"turns":5, "R":1.0, "r":0.2}},
    {"name": "10. Harmonic Lattice", "gen": gen_harmonic_lattice, "params": {"nx":32, "ny":32, "modes":3}},
    {"name": "11. Harmonic Superposition", "gen": gen_harmonic_superposition, "params": {"num_waves":5, "num_points":400}}
]
def get_scene_params(index: int):
    """Return the params dict for the scene index (live reference)."""
    try:
        return scenes[index].setdefault('params', {})
    except Exception:
        return {}


def set_scene_param(index: int, key, value):
    """Set a parameter value for the scene at index (in-place)."""
    try:
        scenes[index].setdefault('params', {})[key] = value
    except Exception:
        pass

# Touch and Android compatibility functions
def get_button_layout():
    """Define touch-friendly button layout for mobile interface."""
    # Make buttons responsive to screen size
    button_height = max(40, HEIGHT // 20)  # At least 40px, but scale with screen
    button_width = max(80, WIDTH // 10)    # At least 80px, but scale with screen
    margin = max(5, WIDTH // 80)           # At least 5px margin
    
    # Calculate button positions that work on different screen sizes
    bottom_row_y = HEIGHT - button_height - margin
    second_row_y = HEIGHT - 2 * (button_height + margin)
    
    buttons = {
        'prev_scene': {'rect': (margin, bottom_row_y, button_width, button_height), 'text': '< Prev'},
        'next_scene': {'rect': (margin + button_width + margin, bottom_row_y, button_width, button_height), 'text': 'Next >'},
        'edit_mode': {'rect': (WIDTH - button_width - margin, bottom_row_y, button_width, button_height), 'text': 'Edit'},
        'auto_rotate': {'rect': (WIDTH - 2 * (button_width + margin), bottom_row_y, button_width, button_height), 'text': 'Auto'},
        'zoom': {'rect': (WIDTH - 3 * (button_width + margin), bottom_row_y, button_width, button_height), 'text': 'Zoom'},
        'save': {'rect': (margin, second_row_y, button_width, button_height), 'text': 'Save'},
        'load': {'rect': (margin + button_width + margin, second_row_y, button_width, button_height), 'text': 'Load'},
        'presets': {'rect': (WIDTH - button_width - margin, second_row_y, button_width, button_height), 'text': 'Presets'},
        'help': {'rect': (WIDTH - 2 * (button_width + margin), second_row_y, button_width, button_height), 'text': 'Help'}
    }
    return buttons

def draw_touch_buttons(screen, font, buttons, current_states):
    """Draw virtual touch buttons with current state indicators."""
    for button_name, button_data in buttons.items():
        rect = button_data['rect']
        text = button_data['text']
        
        # Choose colors based on state
        if button_name == 'auto_rotate' and current_states.get('auto_rotate', True):
            color = GREEN
            bg_color = (0, 64, 0)
        elif button_name == 'edit_mode' and current_states.get('edit_mode', False):
            color = BLUE
            bg_color = (0, 0, 64)
        else:
            color = WHITE
            bg_color = (32, 32, 32)
        
        # Draw button background
        _pygame.draw.rect(screen, bg_color, rect)
        _pygame.draw.rect(screen, color, rect, 2)
        
        # Draw button text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(rect[0] + rect[2]//2, rect[1] + rect[3]//2))
        screen.blit(text_surface, text_rect)

def handle_touch_input(touch_x, touch_y, current_scene, edit_mode, auto_rotate, zoom, preset_browser):
    """Handle touch input on virtual buttons and return action to perform."""
    buttons = get_button_layout()
    
    for button_name, button_data in buttons.items():
        rect = button_data['rect']
        if (rect[0] <= touch_x <= rect[0] + rect[2] and 
            rect[1] <= touch_y <= rect[1] + rect[3]):
            return button_name
    
    return None

def is_mobile_device():
    """Detect if running on mobile device (Android)."""
    try:
        import platform
        import os
        # Check for Android-specific environment variables and properties
        android_indicators = [
            platform.system() == "Linux" and "ANDROID_ROOT" in os.environ,
            hasattr(_pygame, 'FINGERDOWN'),
            os.path.exists('/system/build.prop'),  # Android system file
            'android' in platform.platform().lower()
        ]
        return any(android_indicators)
    except:
        return False

def main():
    screen, clock, font = init_pygame()
    current_scene = 0
    angle_x = angle_y = angle_z = 0.0
    running = True
    edit_mode = False
    edit_keys = []
    edit_index = 0
    auto_rotate = True
    zoom = 1.0
    # Preset browser & help overlay state
    presets_dir = os.path.join(os.path.dirname(__file__), "presets")
    os.makedirs(presets_dir, exist_ok=True)
    preset_browser = False
    preset_list = []
    preset_index = 0
    help_overlay = False
    # slider and text input state
    slider_active = False
    slider_rect = None
    numeric_input_mode = False
    numeric_input_str = ""
    save_name_mode = False
    save_name_str = ""
    rename_mode = False
    rename_str = ""
    tag_mode = False
    tag_str = ""
    # load or initialize preset index metadata
    index_file = os.path.join(presets_dir, "index.json")
    try:
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                presets_index = json.load(f)
        else:
            presets_index = {}
    except Exception:
        presets_index = {}

    while running:
        for event in _pygame.event.get():
            if event.type == _pygame.QUIT:
                running = False
            elif event.type == _pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # start slider drag if inside slider rect
                if slider_rect and (slider_rect[0] <= mx <= slider_rect[0] + slider_rect[2]) and (slider_rect[1] <= my <= slider_rect[1] + slider_rect[3]):
                    slider_active = True
                else:
                    slider_active = False
            elif event.type == _pygame.MOUSEBUTTONUP:
                slider_active = False
            elif event.type == _pygame.MOUSEMOTION and slider_active:
                mx, my = event.pos
                sx, sy, sw, sh = slider_rect
                ratio = max(0.0, min(1.0, (mx - sx) / sw))
                sel = edit_keys[edit_index] if edit_keys else None
                if sel is not None:
                    v = scenes[current_scene]["params"].get(sel)
                    if isinstance(v, int):
                        vmin, vmax = 0, max(20, v * 2 + 1)
                        scenes[current_scene]["params"][sel] = int(round(vmin + ratio * (vmax - vmin)))
                    else:
                        vmin, vmax = -10.0, 10.0
                        scenes[current_scene]["params"][sel] = vmin + ratio * (vmax - vmin)
            
            # Touch event handling for Android
            elif event.type == _pygame.FINGERDOWN:
                # Convert normalized touch coordinates to screen coordinates
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                
                # Handle touch as mouse click for UI elements
                mx, my = touch_x, touch_y
                if slider_rect and (slider_rect[0] <= mx <= slider_rect[0] + slider_rect[2]) and (slider_rect[1] <= my <= slider_rect[1] + slider_rect[3]):
                    slider_active = True
                else:
                    slider_active = False
                    # Check for virtual button touches
                    touch_action = handle_touch_input(touch_x, touch_y, current_scene, edit_mode, auto_rotate, zoom, preset_browser)
                    if touch_action == 'next_scene':
                        current_scene = (current_scene + 1) % len(scenes)
                    elif touch_action == 'prev_scene':
                        current_scene = (current_scene - 1) % len(scenes)
                    elif touch_action == 'edit_mode':
                        edit_mode = not edit_mode
                        edit_index = 0
                        edit_keys = list(scenes[current_scene]["params"].keys())
                    elif touch_action == 'auto_rotate':
                        auto_rotate = not auto_rotate
                    elif touch_action == 'zoom':
                        zoom = 2.0 if zoom == 1.0 else 1.0
                    elif touch_action == 'save':
                        save_name_mode = True
                        save_name_str = ""
                    elif touch_action == 'load':
                        # Load the most recent preset for this scene
                        try:
                            preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                            if preset_list:
                                sel = preset_list[-1]
                                with open(os.path.join(presets_dir, sel), "r") as f:
                                    data = json.load(f)
                                    for k, v in data.items():
                                        if isinstance(v, list):
                                            scenes[current_scene]["params"][k] = np.array(v)
                                        else:
                                            scenes[current_scene]["params"][k] = v
                        except Exception as e:
                            print("Failed to load preset:", e)
                    elif touch_action == 'presets':
                        preset_browser = not preset_browser
                        if preset_browser:
                            preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                            preset_index = 0
                    elif touch_action == 'help':
                        help_overlay = not help_overlay
            
            elif event.type == _pygame.FINGERUP:
                slider_active = False
            
            elif event.type == _pygame.FINGERMOTION and slider_active:
                # Convert normalized touch coordinates to screen coordinates
                touch_x = int(event.x * WIDTH)
                touch_y = int(event.y * HEIGHT)
                mx, my = touch_x, touch_y
                sx, sy, sw, sh = slider_rect
                ratio = max(0.0, min(1.0, (mx - sx) / sw))
                sel = edit_keys[edit_index] if edit_keys else None
                if sel is not None:
                    v = scenes[current_scene]["params"].get(sel)
                    if isinstance(v, int):
                        vmin, vmax = 0, max(20, v * 2 + 1)
                        scenes[current_scene]["params"][sel] = int(round(vmin + ratio * (vmax - vmin)))
                    else:
                        vmin, vmax = -10.0, 10.0
                        scenes[current_scene]["params"][sel] = vmin + ratio * (vmax - vmin)
            
            if event.type == _pygame.KEYDOWN:
                # keyboard text input handling for numeric/save/rename/tag modes
                if numeric_input_mode:
                    if event.key == _pygame.K_RETURN:
                        try:
                            val = float(numeric_input_str)
                            k = edit_keys[edit_index]
                            if isinstance(scenes[current_scene]["params"].get(k), int):
                                scenes[current_scene]["params"][k] = int(round(val))
                            else:
                                scenes[current_scene]["params"][k] = val
                        except Exception:
                            pass
                        numeric_input_mode = False
                        numeric_input_str = ""
                        continue
                    elif event.key == _pygame.K_BACKSPACE:
                        numeric_input_str = numeric_input_str[:-1]
                        continue
                    else:
                        ch = event.unicode
                        if ch and (ch.isdigit() or ch in ".-eE"):
                            numeric_input_str += ch
                        continue
                if save_name_mode:
                    if event.key == _pygame.K_RETURN:
                        # handled above in KEYDOWN handler branch for RETURN
                        pass
                    elif event.key == _pygame.K_BACKSPACE:
                        save_name_str = save_name_str[:-1]
                        continue
                    else:
                        ch = event.unicode
                        if ch:
                            save_name_str += ch
                        continue
                if rename_mode:
                    if event.key == _pygame.K_RETURN:
                        # handled above
                        pass
                    elif event.key == _pygame.K_BACKSPACE:
                        rename_str = rename_str[:-1]
                        continue
                    else:
                        ch = event.unicode
                        if ch:
                            rename_str += ch
                        continue
                if tag_mode:
                    if event.key == _pygame.K_RETURN:
                        # handled above
                        pass
                    elif event.key == _pygame.K_BACKSPACE:
                        tag_str = tag_str[:-1]
                        continue
                    else:
                        ch = event.unicode
                        if ch:
                            tag_str += ch
                        continue
                if event.key == _pygame.K_RIGHT:
                    current_scene = (current_scene + 1) % len(scenes)
                elif event.key == _pygame.K_LEFT:
                    current_scene = (current_scene - 1) % len(scenes)
                elif event.key == _pygame.K_e:
                    # toggle edit mode
                    edit_mode = not edit_mode
                    edit_index = 0
                    edit_keys = list(scenes[current_scene]["params"].keys())
                elif event.key == _pygame.K_TAB:
                    # cycle which param to edit
                    if edit_keys:
                        edit_index = (edit_index + 1) % len(edit_keys)
                elif event.key == _pygame.K_a:
                    auto_rotate = not auto_rotate
                elif event.key == _pygame.K_z:
                    # toggle zoom between 1.0 and 2.0 (2x zoom out)
                    zoom = 2.0 if zoom == 1.0 else 1.0
                elif event.key == _pygame.K_s:
                    # enter save-name mode to allow naming and tagging before saving
                    save_name_mode = True
                    save_name_str = ""
                elif event.key == _pygame.K_p:
                    # toggle preset browser
                    preset_browser = not preset_browser
                    if preset_browser:
                        preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                        preset_index = 0
                elif event.key == _pygame.K_RETURN or event.key == _pygame.K_KP_ENTER:
                    # if entering text modes, finalize input
                    if save_name_mode:
                        # commit save with provided name (fallback to timestamp)
                        try:
                            name = save_name_str.strip() or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                            fname = f"scene_{current_scene}_{name}.json"
                            fpath = os.path.join(presets_dir, fname)
                            with open(fpath, "w") as f:
                                serial = {k: (v.tolist() if hasattr(v, 'tolist') else v) for k, v in scenes[current_scene]["params"].items()}
                                json.dump(serial, f, indent=2)
                            # update index
                            presets_index[fname] = {"scene": current_scene, "name": name, "tags": []}
                            with open(index_file, "w") as f:
                                json.dump(presets_index, f, indent=2)
                            preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                            preset_index = max(0, len(preset_list) - 1)
                        except Exception as e:
                            print("Failed to save preset:", e)
                        save_name_mode = False
                    elif rename_mode and preset_browser and preset_list:
                        sel = preset_list[preset_index]
                        newname = rename_str.strip()
                        if newname:
                            try:
                                newfile = f"scene_{current_scene}_{newname}.json"
                                os.rename(os.path.join(presets_dir, sel), os.path.join(presets_dir, newfile))
                                # update index
                                if sel in presets_index:
                                    presets_index[newfile] = presets_index.pop(sel)
                                    presets_index[newfile]["name"] = newname
                                    with open(index_file, "w") as f:
                                        json.dump(presets_index, f, indent=2)
                                preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                                preset_index = 0
                            except Exception as e:
                                print("Failed to rename preset:", e)
                        rename_mode = False
                    elif tag_mode and preset_browser and preset_list:
                        sel = preset_list[preset_index]
                        tags = [t.strip() for t in tag_str.split(",") if t.strip()]
                        try:
                            if sel not in presets_index:
                                presets_index[sel] = {"scene": current_scene, "name": sel, "tags": tags}
                            else:
                                presets_index[sel]["tags"] = tags
                            with open(index_file, "w") as f:
                                json.dump(presets_index, f, indent=2)
                        except Exception as e:
                            print("Failed to tag preset:", e)
                        tag_mode = False
                    else:
                        # if preset browser open, load selected
                        if preset_browser and preset_list:
                            sel = preset_list[preset_index]
                            try:
                                with open(os.path.join(presets_dir, sel), "r") as f:
                                    data = json.load(f)
                                    for k, v in data.items():
                                        if isinstance(v, list):
                                            scenes[current_scene]["params"][k] = np.array(v)
                                        else:
                                            scenes[current_scene]["params"][k] = v
                            except Exception as e:
                                print("Failed to load preset:", e)
                elif event.key == _pygame.K_d:
                    # delete selected preset when browser open
                    if preset_browser and preset_list:
                        sel = preset_list.pop(preset_index)
                        try:
                            os.remove(os.path.join(presets_dir, sel))
                            if sel in presets_index:
                                presets_index.pop(sel, None)
                                with open(index_file, "w") as f:
                                    json.dump(presets_index, f, indent=2)
                            preset_index = max(0, preset_index - 1)
                        except Exception as e:
                            print("Failed to delete preset:", e)
                elif event.key == _pygame.K_l:
                    # load the most recent preset for this scene if exists
                    try:
                        preset_list = sorted([p for p in os.listdir(presets_dir) if p.startswith(f"scene_{current_scene}_")])
                        if preset_list:
                            sel = preset_list[-1]
                            with open(os.path.join(presets_dir, sel), "r") as f:
                                data = json.load(f)
                                for k, v in data.items():
                                    if isinstance(v, list):
                                        scenes[current_scene]["params"][k] = np.array(v)
                                    else:
                                        scenes[current_scene]["params"][k] = v
                    except Exception as e:
                        print("Failed to load preset:", e)
                elif event.key == _pygame.K_h:
                    help_overlay = not help_overlay
                # Param adjustments (example for p/q in knot scenes)
                if event.key == _pygame.K_UP:
                    if edit_mode and edit_keys:
                        k = edit_keys[edit_index]
                        v = scenes[current_scene]["params"].get(k)
                        if isinstance(v, (int, float)):
                            scenes[current_scene]["params"][k] = v + (1 if isinstance(v, int) else 0.1)
                elif event.key == _pygame.K_DOWN:
                    if edit_mode and edit_keys:
                        k = edit_keys[edit_index]
                        v = scenes[current_scene]["params"].get(k)
                        if isinstance(v, (int, float)):
                            scenes[current_scene]["params"][k] = v - (1 if isinstance(v, int) else 0.1)

        screen.fill((0, 0, 0))

        # Generate points for current scene
        scene = scenes[current_scene]
        # provide a time parameter to generators that support it (e.g., standing wave)
        t = _pygame.time.get_ticks() / 1000.0
        params = dict(scene["params"])
        # Only pass t if the generator supports it (avoid unexpected kwargs)
        try:
            import inspect
            sig = inspect.signature(scene["gen"])
            if "t" in sig.parameters:
                params.setdefault("t", t)
        except Exception:
            pass
        # Filter params to those accepted by the generator to avoid TypeError
        try:
            sig = inspect.signature(scene["gen"])
            accepted = {k: v for k, v in params.items() if k in sig.parameters}
            points = scene["gen"](**accepted)
        except Exception:
            # Fallback: try calling without kwargs
            try:
                points = scene["gen"]()
            except Exception as e:
                raise

        # Rotate and project
        if auto_rotate:
            angle_x += 0.01
            angle_y += 0.02
            angle_z += 0.005
        # Apply rotation uniformly; quaternion-producing generators will already return rotated points if desired
        points = rotate_points(points, angle_x, angle_y, angle_z)
        proj_points = project(points, zoom=zoom)

        # Draw lines/points (sanitize projected points first)
        sanitized = []
        for p in proj_points:
            try:
                px, py = p
                px = int(px); py = int(py)
                sanitized.append((px, py))
            except Exception:
                continue
        if len(sanitized) > 1:
            _pygame.draw.lines(screen, WHITE, False, sanitized, 1)
        elif len(sanitized) == 1:
            _pygame.draw.circle(screen, RED, sanitized[0], 2)

        # Overlay text (scene name + params)
        base = scene["name"] + f" Params: {scene['params']}"
        text = font.render(base, True, GREEN)
        screen.blit(text, (10, 10))
        # Edit mode indicator and selected param
        if edit_mode and edit_keys:
            sel = edit_keys[edit_index]
            val = scenes[current_scene]["params"].get(sel)
            edit_text = f"EDIT MODE: {sel} = {val:.3g}" if isinstance(val, float) else f"EDIT MODE: {sel} = {val}"
            txt2 = font.render(edit_text, True, BLUE)
            screen.blit(txt2, (10, 34))
        else:
            auto_text = f"AUTO_ROTATE: {'ON' if auto_rotate else 'OFF'}  ZOOM: {zoom}x"
            txt2 = font.render(auto_text, True, BLUE)
            screen.blit(txt2, (10, 34))

        # Preset browser overlay
        if preset_browser:
            # semi-transparent background
            overlay_w, overlay_h = 360, 200
            overlay_surf = _pygame.Surface((overlay_w, overlay_h))
            overlay_surf.set_alpha(180)
            overlay_surf.fill((20, 20, 20))
            screen.blit(overlay_surf, (WIDTH - overlay_w - 10, 50))
            # list presets
            for i, fname in enumerate(preset_list[:10]):
                color = GREEN if i == preset_index else WHITE
                txt = font.render(fname, True, color)
                screen.blit(txt, (WIDTH - overlay_w, 60 + i * 18))
            hint = font.render("Enter=Load  D=Delete  S=Save  P=Close", True, BLUE)
            screen.blit(hint, (WIDTH - overlay_w, 60 + 11 * 18))

        # Help overlay
        if help_overlay:
            help_lines = [
                "Keys:",
                "Left/Right: change scene",
                "E: edit params, Tab: next param, Up/Down: change",
                "A: toggle auto-rotate, Z: toggle zoom",
                "S: save preset, P: open preset browser, L: load latest",
                "Enter (in browser): load, D: delete preset",
                "H: toggle this help",
            ]
            hx, hy = 20, HEIGHT - 20 - len(help_lines) * 18
            for i, line in enumerate(help_lines):
                txt = font.render(line, True, BLUE)
                screen.blit(txt, (hx, hy + i * 18))

        # Draw touch buttons for mobile interface
        if is_mobile_device() or True:  # Always show for now, can be mobile-only later
            buttons = get_button_layout()
            current_states = {
                'auto_rotate': auto_rotate,
                'edit_mode': edit_mode
            }
            draw_touch_buttons(screen, font, buttons, current_states)

        _pygame.display.flip()
        clock.tick(60)

    if _pygame is not None:
        _pygame.quit()


if __name__ == "__main__":
    # Avoid running main when imported by test runners like pytest
    try:
        import sys
        if "pytest" not in sys.modules and "PYTEST_CURRENT_TEST" not in os.environ:
            main()
    except Exception:
        main()
