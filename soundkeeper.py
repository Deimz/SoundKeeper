"""
SoundKeeper - Bluetooth Audio Device Keep-Alive Application

Prevents Bluetooth audio devices (soundbars, speakers, headphones) from entering 
standby mode by playing imperceptible audio signals at regular intervals.

Author: Your Name
License: MIT
"""

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import sounddevice as sd
import numpy as np
import threading
import time
import sys
import os
import winreg
import ctypes
from ctypes import wintypes

# Application Configuration
APP_NAME = "SoundKeeper"
SAMPLE_RATE = 44100      # Audio sample rate in Hz
DURATION = 1.0           # Duration of each keep-alive sound in seconds
INTERVAL = 55            # Interval between sounds in seconds (below typical 60s timeout)
AMPLITUDE = 0.0001       # Sound amplitude (very low to be imperceptible)

# Global state variables
running = True
audio_active = True
mutex = None

# --- SINGLE INSTANCE PROTECTION ---

def check_single_instance():
    """
    Ensures only one instance of the application runs at a time.
    Uses Windows mutex to prevent multiple instances.
    
    Returns:
        bool: True if this is the only instance, False otherwise
    """
    global mutex
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "Global\\SoundKeeperMutex")
    last_error = ctypes.windll.kernel32.GetLastError()
    
    # ERROR_ALREADY_EXISTS = 183
    if last_error == 183:
        ctypes.windll.user32.MessageBoxW(
            0,
            "SoundKeeper is already running!",
            "Instance Already Active",
            0x30  # MB_ICONWARNING
        )
        return False
    return True

# --- WINDOWS STARTUP MANAGEMENT ---

def get_startup_status():
    """
    Checks if the application is registered in Windows startup.
    
    Returns:
        bool: True if registered in startup, False otherwise
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 
                             0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        key.Close()
        return True
    except FileNotFoundError:
        return False

def toggle_startup(icon, item):
    """
    Toggles the application's Windows startup registration.
    Adds or removes the application from the Windows registry Run key.
    """
    is_enabled = get_startup_status()
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        if is_enabled:
            # Remove from startup
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        else:
            # Add to startup - sys.executable returns the full path to the .exe
            exe_path = sys.executable
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            
        key.Close()
    except Exception as e:
        print(f"Registry error: {e}")

# --- AUDIO & UI FUNCTIONS ---

def create_icon_image(color):
    """
    Creates a simple colored icon for the system tray.
    
    Args:
        color (str): Color name (e.g., 'green', 'grey')
    
    Returns:
        PIL.Image: Generated icon image
    """
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color)
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill="white")
    return image

def play_keep_alive_sound():
    """
    Continuously plays imperceptible audio signals to keep Bluetooth devices active.
    Runs in a separate daemon thread and respects the audio_active flag.
    """
    while running:
        if audio_active:
            try:
                # Generate white noise with very low amplitude
                noise = np.random.uniform(-AMPLITUDE, AMPLITUDE, 
                                        (int(SAMPLE_RATE * DURATION), 2)).astype(np.float32)
                sd.play(noise, SAMPLE_RATE)
                sd.wait()
            except Exception:
                pass
        
        # Wait for the specified interval
        for _ in range(INTERVAL):
            if not running:
                break
            time.sleep(1)

def toggle_activation(icon, item):
    """
    Toggles the keep-alive audio functionality on/off.
    Updates the icon color to reflect the current state.
    """
    global audio_active
    audio_active = not audio_active
    new_color = "green" if audio_active else "grey"
    icon.icon = create_icon_image(new_color)

def quit_app(icon, item):
    """
    Gracefully exits the application.
    Stops the audio thread and removes the system tray icon.
    """
    global running
    running = False
    icon.stop()

def setup(icon):
    """
    Initializes the system tray icon visibility.
    """
    icon.visible = True

# --- APPLICATION ENTRY POINT ---

# Ensure only one instance is running
if not check_single_instance():
    sys.exit(0)

# Define the system tray menu
menu = (
    item('Active (Keep-Alive)', toggle_activation, checked=lambda item: audio_active),
    item('Launch at Startup', toggle_startup, checked=lambda item: get_startup_status()),
    item(pystray.Menu.SEPARATOR, None),
    item('Quit', quit_app)
)

# Start the audio keep-alive thread
audio_thread = threading.Thread(target=play_keep_alive_sound)
audio_thread.daemon = True
audio_thread.start()

# Initialize and run the system tray icon
image = create_icon_image("green")
icon = pystray.Icon("SoundKeeper", image, "SoundKeeper", menu)
icon.run(setup)
