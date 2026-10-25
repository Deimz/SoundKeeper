"""Keep audio devices awake with quiet, periodic noise and a Windows tray menu."""

import ctypes
import subprocess
import sys
import threading
import time
import winreg
from ctypes import wintypes
from dataclasses import replace
from pathlib import Path

import numpy as np
import pystray
import sounddevice as sd
from PIL import Image, ImageDraw
from pystray import MenuItem as item

from settings import (
    DURATION_OPTIONS,
    LANGUAGE_NAMES,
    WAIT_OPTIONS,
    Settings,
    config_path,
    load_settings,
    save_settings,
)
from translations import preferred_ui_languages, resolve_language, translate

APP_NAME = "SoundKeeper"
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def initialize_dpi_awareness():
    """Configure source runs before any UI; respect an existing host/EXE policy."""
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
    except OSError:
        return

    try:
        set_context = user32.SetProcessDpiAwarenessContext
        set_context.argtypes = (ctypes.c_void_p,)
        set_context.restype = wintypes.BOOL
        if set_context(ctypes.c_void_p(-4)):  # PER_MONITOR_AWARE_V2
            return
        if ctypes.get_last_error() == 5:  # Already set by manifest or host.
            return
    except (AttributeError, OSError):
        pass

    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        set_awareness = shcore.SetProcessDpiAwareness
        set_awareness.argtypes = (ctypes.c_int,)
        set_awareness.restype = ctypes.c_long  # HRESULT
        result = set_awareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        if result == 0 or result & 0xFFFFFFFF == 0x80070005:
            return  # Success, or DPI awareness was already configured.
    except (AttributeError, OSError):
        pass

    try:
        set_system_aware = user32.SetProcessDPIAware
        set_system_aware.argtypes = ()
        set_system_aware.restype = wintypes.BOOL
        set_system_aware()
    except (AttributeError, OSError):
        pass  # DPI support must not prevent audio keep-alive from starting.


def check_single_instance(language):
    """Return a mutex handle, or None when another instance already exists."""
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = (ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    handle = kernel32.CreateMutexW(None, False, "Global\\SoundKeeperMutex")
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(handle)
        ctypes.windll.user32.MessageBoxW(
            0, translate(language, "already_running"), APP_NAME, 0x30
        )
        return None
    return handle


def get_startup_status():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except OSError:
        return False


def startup_command():
    """Quote paths and include the script when running without PyInstaller."""
    arguments = [sys.executable]
    if not getattr(sys, "frozen", False):
        windowed = Path(sys.executable).with_name("pythonw.exe")
        if windowed.exists():
            arguments[0] = str(windowed)
        arguments.append(str(Path(__file__).resolve()))
    return subprocess.list2cmdline(arguments)


def create_icon_image(color):
    image = Image.new("RGB", (64, 64), color)
    ImageDraw.Draw(image).ellipse((16, 16, 48, 48), fill="white")
    return image


class AudioOutput:
    """Cache a validated format; invalidate it when the device changes or fails."""

    def __init__(self):
        self.device_key = None
        self.samplerate = None

    def invalidate(self):
        self.device_key = None
        self.samplerate = None

    def select_format(self, sample_rate="auto"):
        device = sd.query_devices(kind="output")
        key = (
            device["index"],
            device["name"],
            device["hostapi"],
            device["default_samplerate"],
            device["max_output_channels"],
            sample_rate,
        )
        if key == self.device_key:
            return device["index"], self.samplerate
        rates = (
            dict.fromkeys((device["default_samplerate"], 44100, 48000))
            if sample_rate == "auto"
            else (sample_rate,)
        )
        for rate in rates:
            if not np.isfinite(rate) or rate <= 0:
                continue
            try:
                sd.check_output_settings(
                    device=device["index"], channels=2, dtype="float32", samplerate=rate
                )
            except sd.PortAudioError:
                continue
            self.device_key = key
            self.samplerate = rate
            return device["index"], rate
        self.invalidate()
        raise sd.PortAudioError("No supported stereo output sample rate")

    def play(self, duration, amplitude, sample_rate):
        try:
            device, rate = self.select_format(sample_rate)
            noise = np.random.uniform(
                -amplitude, amplitude, (max(1, int(rate * duration)), 2)
            ).astype(np.float32)
            sd.play(noise, rate, device=device)
            sd.wait()
        except Exception:
            self.invalidate()
            raise


class SoundKeeper:
    def __init__(self, path=None):
        self.path = config_path() if path is None else path
        self.settings = load_settings(self.path)
        self.system_languages = preferred_ui_languages()
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.stopped = threading.Event()
        self.audio_active = True
        self.audio_error = False
        self.output = AudioOutput()
        self.icon = pystray.Icon(APP_NAME, create_icon_image("green"), APP_NAME)
        self.icon.menu = self.create_menu()

    def text(self, key, **values):
        language = resolve_language(self.settings.language, self.system_languages)
        return translate(language, key, **values)

    def duration_text(self, seconds):
        if seconds < 60:
            return self.text("seconds", value=f"{seconds:g}")
        minutes, remainder = divmod(seconds, 60)
        return self.text("minutes", minutes=int(minutes), seconds=f"{remainder:g}")

    def refresh_icon(self):
        with self.lock:
            active, error = self.audio_active, self.audio_error
        color = "orange" if active and error else "green" if active else "grey"
        self.icon.icon = create_icon_image(color)
        self.icon.title = self.text("audio_error") if active and error else APP_NAME
        self.icon.update_menu()

    def persist_settings(self):
        try:
            save_settings(self.path, self.settings)
        except OSError:
            self.icon.notify(self.text("save_error"), APP_NAME)

    def change_setting(self, name, value):
        def callback(icon, menu_item):
            with self.lock:
                self.settings = replace(self.settings, **{name: value})
            self.persist_settings()
            if name != "language":
                self.wake.set()
            self.refresh_icon()

        return callback

    def reset_settings(self, icon, menu_item):
        defaults = Settings()
        with self.lock:
            self.settings = replace(
                self.settings,
                wait_seconds=defaults.wait_seconds,
                duration_seconds=defaults.duration_seconds,
            )
        self.persist_settings()
        self.wake.set()
        self.refresh_icon()

    def options_menu(self, name, values):
        return pystray.Menu(
            *(
                item(
                    lambda menu_item, value=value: self.duration_text(value),
                    self.change_setting(name, value),
                    checked=lambda menu_item, value=value: (
                        getattr(self.settings, name) == value
                    ),
                    radio=True,
                )
                for value in values
            ),
            item(
                lambda menu_item: self.duration_text(getattr(self.settings, name)),
                None,
                checked=lambda menu_item: True,
                radio=True,
                enabled=False,
                visible=lambda menu_item: getattr(self.settings, name) not in values,
            ),
        )

    def create_menu(self):
        languages = {"auto": None, **LANGUAGE_NAMES}
        language_menu = pystray.Menu(
            *(
                item(
                    (lambda menu_item: self.text("auto")) if code == "auto" else name,
                    self.change_setting("language", code),
                    checked=lambda menu_item, code=code: self.settings.language == code,
                    radio=True,
                )
                for code, name in languages.items()
            )
        )
        return pystray.Menu(
            item(
                lambda menu_item: self.text("active"),
                self.toggle_activation,
                checked=lambda menu_item: self.audio_active,
            ),
            item(
                lambda menu_item: self.text("startup"),
                self.toggle_startup,
                checked=lambda menu_item: get_startup_status(),
            ),
            item(
                lambda menu_item: self.text("settings"),
                pystray.Menu(
                    item(
                        lambda menu_item: self.text("wait"),
                        self.options_menu("wait_seconds", WAIT_OPTIONS),
                    ),
                    item(
                        lambda menu_item: self.text("duration"),
                        self.options_menu("duration_seconds", DURATION_OPTIONS),
                    ),
                    pystray.Menu.SEPARATOR,
                    item(lambda menu_item: self.text("reset"), self.reset_settings),
                ),
            ),
            item(lambda menu_item: self.text("language"), language_menu),
            item(
                lambda menu_item: self.text("audio_error"),
                None,
                enabled=False,
                visible=lambda menu_item: self.audio_active and self.audio_error,
            ),
            pystray.Menu.SEPARATOR,
            item(lambda menu_item: self.text("quit"), self.quit),
        )

    def toggle_activation(self, icon, menu_item):
        with self.lock:
            self.audio_active = not self.audio_active
        self.wake.set()
        self.refresh_icon()

    def toggle_startup(self, icon, menu_item):
        try:
            enabled = get_startup_status()
            with winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_SET_VALUE
            ) as key:
                if enabled:
                    winreg.DeleteValue(key, APP_NAME)
                else:
                    winreg.SetValueEx(
                        key, APP_NAME, 0, winreg.REG_SZ, startup_command()
                    )
        except OSError:
            self.icon.notify(self.text("startup_error"), APP_NAME)

    def set_audio_error(self, error):
        with self.lock:
            changed = self.audio_error != error
            self.audio_error = error
        if changed and not self.stopped.is_set():
            self.refresh_icon()

    def play_keep_alive_sound(self):
        while not self.stopped.is_set():
            self.wake.clear()
            with self.lock:
                settings, active = self.settings, self.audio_active
            if self.stopped.is_set():
                break
            if not active:
                self.wake.wait()
                continue
            try:
                self.output.play(
                    settings.duration_seconds, settings.amplitude, settings.sample_rate
                )
                self.set_audio_error(False)
            except Exception:
                self.set_audio_error(True)
            if self.stopped.is_set():
                break
            if self.audio_error:
                # Long user intervals must not delay recovery after an audio failure.
                self.wake.wait(5)
                continue

            # The interval starts after playback, rather than between playback starts.
            deadline = time.monotonic() + settings.wait_seconds
            while not self.stopped.is_set():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                if self.wake.wait(remaining):
                    self.wake.clear()
                    with self.lock:
                        active = self.audio_active
                        settings = self.settings
                    if not active:
                        break
                    deadline = time.monotonic() + settings.wait_seconds

    def quit(self, icon, menu_item):
        self.stopped.set()
        self.wake.set()
        sd.stop()
        icon.stop()

    def run(self):
        def setup(icon):
            icon.visible = True
            self.persist_settings()
            worker.start()

        worker = threading.Thread(target=self.play_keep_alive_sound, daemon=True)
        try:
            self.icon.run(setup)
        finally:
            self.stopped.set()
            self.wake.set()
            sd.stop()
            if worker.ident is not None:
                worker.join(timeout=5)


def main():
    initialize_dpi_awareness()
    path = config_path()
    settings = load_settings(path)
    language = resolve_language(settings.language, preferred_ui_languages())
    mutex = check_single_instance(language)
    if mutex is None:
        return
    try:
        SoundKeeper(path).run()
    finally:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL
        kernel32.CloseHandle(mutex)


if __name__ == "__main__":
    main()
