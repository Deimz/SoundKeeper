# SoundKeeper

**English** · [简体中文](README.zh-CN.md)

Keep audio devices awake with quiet, periodic noise and a Windows system tray menu.

This version extends [Deimz/SoundKeeper](https://github.com/Deimz/SoundKeeper), the
original project by Deimz, with saved preferences, six interface languages, and
automatic sample-rate selection. Thank you to the upstream author and contributors.
The changes are proposed in [upstream PR #1](https://github.com/Deimz/SoundKeeper/pull/1).

[Fork releases](https://github.com/Jazzwind/SoundKeeper/releases) ·
[Upstream project](https://github.com/Deimz/SoundKeeper) ·
[Report an issue](https://github.com/Jazzwind/SoundKeeper/issues)

## 📖 About

**SoundKeeper** is a lightweight Windows application that helps prevent audio devices from entering standby mode due to inactivity.

Some soundbars, speakers, and headphones enter standby after a period without
audio. SoundKeeper periodically plays very low-amplitude white noise through the
default output device. Effectiveness and audibility depend on the device, volume,
and timing; there is no universal standby timeout or guaranteed keep-alive setting.

## Compared with upstream

The table compares this fork with [upstream commit `7c1fde4`](https://github.com/Deimz/SoundKeeper/tree/7c1fde480cac87edae8d88cc1ba674d4e1868585),
the version this fork started from. It does not imply that later upstream versions
will lack these improvements.

| Area | Upstream baseline | This fork |
| --- | --- | --- |
| Interface languages | No language selector or system-language matching | Follow Windows UI preferences or choose English, Simplified Chinese, French, Russian, Spanish, or Arabic |
| Timing controls | Edit constants in Python source | Five wait presets, three sound-duration presets, timing reset, and custom JSON values |
| Persistent preferences | No separate preference file | Save and restore preferences in the current user's `config.json` |
| Advanced configuration | Edit four constants in `soundkeeper.py` | Centralized source defaults plus validated JSON overrides for timing, amplitude, sample rate, and language |
| Sample rate | Fixed source constant | Validate the device default with 44100/48000 Hz fallbacks, or validate a manually specified rate |
| Playback failures | Exceptions are silently ignored | Orange tray icon, error status, and retries every five seconds |
| High-DPI menus | No explicit DPI initialization or packaged DPI declaration | Per-Monitor V2 manifest and early source initialization with older-system fallbacks |
| Documentation | English README | English-first bilingual homepage and standalone English/Chinese guides |

Quiet periodic playback, native Windows tray menus, activation/pause, startup
registration, and single-instance protection come from the original project.
The default sound duration (1 second), wait (55 seconds after playback), and
amplitude (0.0001) are preserved. Device compatibility still requires testing.

## ✨ Features

- 🔇 **Imperceptible Audio** - Plays white noise at a very low default amplitude
- ⏱️ **Configurable Timing** - Choose the wait duration and sound duration from the tray menu
- 🎯 **System Tray Integration** - Minimalist interface accessible from the taskbar
- ✅ **Easy Toggle** - Enable/disable with a single click
- 🚀 **Startup Option** - Configure to launch automatically with Windows
- 🌍 **Languages** - Follow the Windows UI language or choose English, Chinese, French, Russian, Spanish, or Arabic
- 💾 **Saved Preferences** - Keep your timing and language preferences across restarts
- 🛡️ **Single Instance** - Prevents multiple instances from running simultaneously
- 🪶 **Lightweight** - Tray settings use the existing dependencies, without an additional GUI framework

## 📥 Download & Installation

### 💻 For Regular Users (Recommended)

A packaged Windows executable does not require a separate Python installation.

1. Open this fork's [Releases page](https://github.com/Jazzwind/SoundKeeper/releases).
2. If a release is available, download its attached executable or portable ZIP.
3. Extract a ZIP before use, then run `SoundKeeper.exe` from a permanent folder.
4. Right-click the green tray icon to configure timing, language, or startup.

If no release is listed, build the current source using the instructions below.
GitHub's automatically generated **Source code** ZIP is not a compiled application.
An upstream release may not include this fork's tray settings or translations.
Exit any older SoundKeeper instance before launching a replacement. Preferences
remain in `%APPDATA%\SoundKeeper\config.json` when the executable is replaced.

---

### 👨‍💻 For Developers (Run from Source)

If you want to modify the code or contribute to the project:

**Requirements:**
- Python 3.9 or higher (dependency versions must support the chosen Python version)
- Windows OS

**Installation Steps:**

```powershell
# Clone the repository
git clone --branch tray-settings-and-localization https://github.com/Jazzwind/SoundKeeper.git
cd SoundKeeper

# Create virtual environment
python -m venv .venv

# Use this environment explicitly; activation is not required
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Run the application
.\.venv\Scripts\python.exe soundkeeper.py
```

## 🎮 Usage

### Quick Start

1. **Launch SoundKeeper** - Double-click `SoundKeeper.exe`
2. **Look for the icon** - A green icon appears in your system tray
3. **Check the device** - Verify that it stays awake past its usual standby timeout

### System Tray Menu

Right-click the icon to access:

- **✅ Active (Keep-Alive)** - Toggle the keep-alive feature on/off
  - 🟢 Green icon = Active
  - ⚫ Grey icon = Paused
- **🚀 Launch at Startup** - Register/unregister from Windows startup
- **❌ Quit** - Exit the application
- **⚙️ Settings** - Choose the wait duration and sound duration, or restore their defaults
- **🌍 Language** - Follow the system or select one of the six supported languages

An orange icon and an audio status message indicate a playback failure. SoundKeeper
rechecks the output format and retries every five seconds until playback succeeds.

### Compatible Devices

Potential uses include these audio devices; compatibility must be checked on the actual device:

- ✅ **Soundbars** (Samsung, LG, Sony, etc.) - Especially TV soundbars used with PCs
- ✅ **Bluetooth Speakers** - Portable or desktop speakers with power-saving modes
- ✅ **Wireless Headphones** - Any brand with aggressive auto-sleep features
- ✅ **Home Theater Systems** - Bluetooth-enabled receivers and amplifiers
- ✅ **Smart Speakers** - When used in Bluetooth mode

## ⚙️ Configuration

Use the tray menu to change preferences without editing source code or rebuilding:

| Setting | Options | Default |
| --- | --- | --- |
| Wait duration | 30 s, 55 s, 4 min 55 s, 9 min 55 s, 14 min 55 s | 55 s |
| Sound duration | 0.01 s, 0.1 s, 1 s | 1 s |
| Language | Follow system, English, Simplified Chinese, French, Russian, Spanish, Arabic | Follow system |

### Source defaults

Advanced users can customize the default configuration in the clearly marked
source-defaults section near the top of `settings.py` before running from source
or building an executable:

```python
DEFAULT_SAMPLE_RATE = "auto"  # Or a supported integer sample rate, e.g. 48000
DEFAULT_DURATION = 1.0
DEFAULT_INTERVAL = 55
DEFAULT_AMPLITUDE = 0.0001
DEFAULT_LANGUAGE = "auto"
```

On first launch, these defaults are used to create the JSON configuration. Valid
existing JSON fields take precedence over source defaults, including after an exe
upgrade. Missing or invalid fields use the corresponding source default.

The wait starts **after playback finishes**. With the defaults, playback starts
approximately every 56 seconds. Changing an audio preference during a wait starts
a new wait using the selected duration; an in-progress sound finishes normally.
Resuming from pause plays immediately. Longer waits must remain shorter than your
device's standby timeout. Very short sounds may not keep every device awake.

### JSON preferences

Preferences are stored per Windows user in `%APPDATA%\SoundKeeper\config.json`.
Exit the app before editing this file, then restart to apply custom values:

```json
{
  "wait_seconds": 55,
  "duration_seconds": 1.0,
  "amplitude": 0.0001,
  "sample_rate": "auto",
  "language": "auto"
}
```

JSON timings are not limited to menu presets. For example, `wait_seconds: 45` and
`duration_seconds: 0.5` are valid. A custom timing value appears as a checked,
read-only menu entry until a preset is selected. Menu changes preserve amplitude
and sample-rate preferences. No input window or amplitude/sample-rate menu is added.

| JSON field | Accepted values |
| --- | --- |
| `wait_seconds` | Number from 0.1 to 86400 seconds |
| `duration_seconds` | Number from 0.001 to 10 seconds |
| `amplitude` | Number from 0 to 1; larger values may be audible |
| `sample_rate` | `"auto"`, or an integer from 8000 to 192000 Hz supported by the output device |

These ranges bound audio allocations and reject invalid numbers. They do not
guarantee that every combination keeps a particular device awake. Source defaults
should also use values within these ranges. Legacy `version` fields are ignored
and omitted when the config is next saved.

For a fixed 48000 Hz rate and French menus, change these JSON fields:

```json
{
  "sample_rate": 48000,
  "language": "fr"
}
```

This is a partial example: other fields may be retained in your existing config.
Use an unquoted integer for a fixed rate (`48000`, not `"48000"` or `48000.0`).
Use the quoted string `"auto"` for automatic selection. Invalid values fall back to
source defaults; a valid fixed rate that the device does not support produces an
audio error. In `settings.py`, the equivalent assignments are
`DEFAULT_SAMPLE_RATE = 48000` and `DEFAULT_LANGUAGE = "fr"`.
JSON does not allow comments; do not add `#` or `//` annotations to the config file.

Language codes are `auto`, `en`, `zh-Hans`, `fr`, `ru`, `es`, and `ar`.
They mean Follow system, English, Simplified Chinese, French, Russian, Spanish,
and Arabic, respectively. Language codes must remain quoted strings in both JSON
and Python.
Follow system checks the Windows preferred UI languages in order and uses the first
supported language family. Unsupported lists fall back to English; all Chinese
variants currently use the Simplified Chinese translation. Language changes update
the menu immediately. Language names are displayed in their own languages.

Missing or invalid preferences use defaults. Settings are saved by atomic file
replacement; a write failure is reported and changes remain usable for the current
session. Restore defaults resets only the two timing preferences to the defaults
bundled with the executable, preserving language, amplitude, sample-rate selection,
and Windows startup registration. Each launch starts with keep-alive enabled.

With `sample_rate: "auto"`, validate the current output device's
default rate for stereo `float32` audio, then try 44100 and 48000 Hz if necessary,
skipping duplicate candidates. The selected rate is used both to generate the
samples and to play them. It is cached until the reported device changes or playback
fails. Only the requested `"auto"` or fixed rate is saved, not the detected rate.
A fixed rate is checked and used as specified; if unsupported, the app reports an
audio error rather than silently selecting another rate. Detection does not change Windows audio
settings or verify a device's standby behavior. Some drivers require an application
restart after devices are connected or disconnected to refresh their device list.

Noise amplitude defaults to `0.0001`. There is no manual
input window or additional GUI dependency. Autostart remains managed by the Windows
Run registry key rather than the JSON file.

## 🔧 Building from Source

To create your own executable:

```powershell
# Install PyInstaller
.\.venv\Scripts\python.exe -m pip install pyinstaller

# Build the executable
.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --manifest=SoundKeeper.manifest --icon=icon.ico --name SoundKeeper soundkeeper.py

# Alternatively, use the checked-in portable build specification
.\.venv\Scripts\python.exe -m PyInstaller SoundKeeper.spec

# Find your .exe in the dist/ folder
```

## 🐛 Troubleshooting

### High-DPI menus

The packaged executable declares Per-Monitor V2 DPI awareness, with fallbacks for
older Windows versions. Source runs initialize DPI awareness before creating any
tray windows or message boxes and preserve an existing host DPI policy. Both build
commands above use the same manifest. Menus continue to use pystray's native Win32
backend and Windows-drawn text; no custom font sizing or GUI dependency is added.

The manifest also preserves normal-user execution, Windows compatibility, Common
Controls v6, and long-path support. DPI initialization failures do not prevent the
keep-alive application from starting. Test builds should be checked at the target
display scaling; mixed-DPI multi-monitor behavior is not guaranteed by the manifest
alone. This change does not alter audio parameters or saved preferences.

### The audio device still disconnects

- Make sure SoundKeeper is running (check system tray)
- Verify the feature is enabled (icon should be green)
- Select a shorter wait duration in the tray settings
- If using a very short sound, try restoring the default 1-second duration
- If the icon is orange, check that an output device is available; restart the app after reconnecting if necessary

### "SoundKeeper is already running" error

- Only one instance can run at a time
- Check the system tray for an existing icon
- Close it before launching again

### Icon doesn't appear in system tray

- Check Windows notification area settings
- Make sure the application hasn't crashed (check Task Manager)

## Development checks

Run regression tests from the repository root after installing `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/SyncReadme.py --check
```

Tests use temporary configuration files and mocked audio/registry operations. They
do not play sound or change your Windows startup registration. Actual Bluetooth
standby behavior and Arabic menu rendering should also be checked on Windows before
publishing a release. Build size and memory use depend on dependency and driver versions.

### Maintaining the bilingual homepage

`README.md` defaults to English. Select **简体中文** at the top to reveal Chinese
on the same page; select **English** to switch back. Modern browsers support the
named, mutually exclusive disclosure sections. Older browsers can expand/collapse
the language headings manually. This does not change the application's language.

Edit `README.en.md` and `README.zh-CN.md`, then run:

```powershell
.\.venv\Scripts\python.exe scripts/SyncReadme.py
```

The standalone guides also work as offline release documentation. Documentation
changes do not require rebuilding the executable.

## 📋 System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** Depends on the Python, dependency, and audio-driver versions
- **Download:** The locally verified portable executable is approximately 28.18 MiB; other builds may differ. One-file builds also need temporary disk space to extract their runtime.
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
- Original icon generated with Gemini, as credited by the upstream project

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/Jazzwind/SoundKeeper/issues)
- **Upstream:** [Deimz/SoundKeeper](https://github.com/Deimz/SoundKeeper)

---

<div align="center">

**If SoundKeeper helped you, please consider giving it a ⭐ on GitHub!**

Made with ❤️ for frustrated Bluetooth users everywhere

</div>
