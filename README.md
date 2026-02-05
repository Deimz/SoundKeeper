# 🔊 SoundKeeper - Bluetooth Audio Device Keep-Alive

<div align="center">

![GitHub release](https://img.shields.io/github/v/release/yourusername/soundkeeper)
![License](https://img.shields.io/github/license/yourusername/soundkeeper)
![Platform](https://img.shields.io/badge/platform-Windows-blue)

**Keep your Bluetooth audio devices connected and active**

[Download Latest Release](https://github.com/yourusername/soundkeeper/releases/latest) | [Report Bug](https://github.com/yourusername/soundkeeper/issues) | [Request Feature](https://github.com/yourusername/soundkeeper/issues)

</div>

---

## � About

**SoundKeeper** is a lightweight Windows application that prevents Bluetooth audio devices (soundbars, speakers, headphones) from automatically entering standby mode due to inactivity. 

Many Bluetooth audio devices, especially those designed for TVs like Samsung soundbars, automatically disconnect or enter standby mode after ~60 seconds of silence. This can be frustrating when using them with a PC. SoundKeeper solves this problem by playing imperceptible audio signals at regular intervals, keeping your device active and connected.

## ✨ Features

- � **Imperceptible Audio** - Plays white noise at extremely low volume (completely inaudible)
- ⏱️ **Smart Timing** - Sends keep-alive signals every 55 seconds (before typical 60s timeout)
- 🎯 **System Tray Integration** - Minimalist interface accessible from the taskbar
- ✅ **Easy Toggle** - Enable/disable with a single click
- 🚀 **Startup Option** - Configure to launch automatically with Windows
- �️ **Single Instance** - Prevents multiple instances from running simultaneously
- 🪶 **Lightweight** - Minimal resource usage (~25MB RAM)

## � Download & Installation

### Option 1: Download Pre-built Executable (Recommended)

1. Go to the [**Releases page**](https://github.com/yourusername/soundkeeper/releases/latest)
2. Download `SoundKeeper.exe` from the latest release
3. Run the executable - no installation required!
4. *Optional:* Right-click the system tray icon and enable "Launch at Startup"

### Option 2: Run from Source

**Requirements:**
- Python 3.7 or higher
- Windows OS

**Installation Steps:**

```powershell
# Clone the repository
git clone https://github.com/yourusername/soundkeeper.git
cd soundkeeper

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python soundkeeper.py
```

## 🎮 Usage

### Quick Start

1. **Launch SoundKeeper** - Double-click `SoundKeeper.exe`
2. **Look for the icon** - A green Bluetooth icon appears in your system tray
3. **It's working!** - Your audio device will now stay connected

### System Tray Menu

Right-click the icon to access:

- **✅ Active (Keep-Alive)** - Toggle the keep-alive feature on/off
  - 🟢 Green icon = Active
  - ⚫ Grey icon = Paused
- **🚀 Launch at Startup** - Register/unregister from Windows startup
- **❌ Quit** - Exit the application

### When to Use

- ✅ **TV Soundbars** connected to PC via Bluetooth
- ✅ **Bluetooth Speakers** that auto-disconnect
- ✅ **Wireless Headphones** with aggressive power-saving
- ✅ Any Bluetooth audio device with standby timeout issues

## ⚙️ Configuration

Advanced users can modify settings in `soundkeeper.py`:

```python
SAMPLE_RATE = 44100    # Audio sample rate in Hz
DURATION = 1.0         # Keep-alive sound duration (seconds)
INTERVAL = 55          # Interval between signals (seconds)
AMPLITUDE = 0.0001     # Sound volume (very low = imperceptible)
```

## � Building from Source

To create your own executable:

```powershell
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --icon=icon.ico --name SoundKeeper soundkeeper.py

# Find your .exe in the dist/ folder
```

## 🐛 Troubleshooting

### The audio device still disconnects

- Make sure SoundKeeper is running (check system tray)
- Verify the feature is enabled (icon should be green)
- Try reducing `INTERVAL` to 45 seconds in the configuration

### "SoundKeeper is already running" error

- Only one instance can run at a time
- Check the system tray for an existing icon
- Close it before launching again

### Icon doesn't appear in system tray

- Check Windows notification area settings
- Make sure the application hasn't crashed (check Task Manager)

## 📋 System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** ~25MB
- **Storage:** ~30MB
- **Audio:** Any audio output device

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📖 Improve documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [pystray](https://github.com/moses-palmer/pystray) for system tray integration
- Audio handling powered by [sounddevice](https://python-sounddevice.readthedocs.io/)
- Icon design inspired by Bluetooth connectivity

## � Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/soundkeeper/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/soundkeeper/discussions)

---

<div align="center">

**If SoundKeeper helped you, please consider giving it a ⭐ on GitHub!**

Made with ❤️ for frustrated Bluetooth users everywhere

</div>
