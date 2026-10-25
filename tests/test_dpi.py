"""DPI initialization tests without changing the test runner's real DPI mode."""

import ctypes
import unittest
from unittest.mock import Mock, patch

import soundkeeper


class DpiTests(unittest.TestCase):
    def setUp(self):
        self.user32 = Mock()
        self.shcore = Mock()
        self.loader = patch(
            "soundkeeper.ctypes.WinDLL",
            side_effect=lambda name, **kwargs: {
                "user32": self.user32,
                "shcore": self.shcore,
            }[name],
        ).start()
        self.error = patch("soundkeeper.ctypes.get_last_error", return_value=87).start()
        self.addCleanup(patch.stopall)

    def test_per_monitor_v2_success_does_not_call_fallbacks(self):
        self.user32.SetProcessDpiAwarenessContext.return_value = True
        soundkeeper.initialize_dpi_awareness()
        argument = self.user32.SetProcessDpiAwarenessContext.call_args.args[0]
        self.assertEqual(argument.value, ctypes.c_void_p(-4).value)
        self.assertEqual(self.loader.call_count, 1)
        self.user32.SetProcessDPIAware.assert_not_called()

    def test_existing_manifest_or_host_policy_is_preserved(self):
        self.user32.SetProcessDpiAwarenessContext.return_value = False
        self.error.return_value = 5
        soundkeeper.initialize_dpi_awareness()
        self.assertEqual(self.loader.call_count, 1)
        self.user32.SetProcessDPIAware.assert_not_called()

    def test_unsupported_v2_falls_back_to_per_monitor(self):
        self.user32.SetProcessDpiAwarenessContext.return_value = False
        self.shcore.SetProcessDpiAwareness.return_value = 0
        soundkeeper.initialize_dpi_awareness()
        self.shcore.SetProcessDpiAwareness.assert_called_once_with(2)
        self.user32.SetProcessDPIAware.assert_not_called()

    def test_missing_v2_api_falls_back_to_per_monitor(self):
        del self.user32.SetProcessDpiAwarenessContext
        self.shcore.SetProcessDpiAwareness.return_value = 0
        soundkeeper.initialize_dpi_awareness()
        self.shcore.SetProcessDpiAwareness.assert_called_once_with(2)

    def test_older_api_also_respects_existing_policy(self):
        self.user32.SetProcessDpiAwarenessContext.return_value = False
        for result in (-2147024891, 0x80070005):
            with self.subTest(hresult=result):
                self.shcore.SetProcessDpiAwareness.return_value = result
                soundkeeper.initialize_dpi_awareness()
        self.user32.SetProcessDPIAware.assert_not_called()

    def test_missing_per_monitor_api_falls_back_to_system(self):
        del self.user32.SetProcessDpiAwarenessContext
        del self.shcore.SetProcessDpiAwareness
        soundkeeper.initialize_dpi_awareness()
        self.user32.SetProcessDPIAware.assert_called_once_with()

    def test_dll_unavailable_does_not_raise(self):
        self.loader.side_effect = OSError("unavailable")
        soundkeeper.initialize_dpi_awareness()

    def test_all_calls_fail_without_preventing_startup(self):
        self.user32.SetProcessDpiAwarenessContext.return_value = False
        self.shcore.SetProcessDpiAwareness.return_value = -2147024809
        self.user32.SetProcessDPIAware.side_effect = OSError("unavailable")
        events = []
        with (
            patch(
                "soundkeeper.config_path", side_effect=lambda: events.append("config")
            ),
            patch("soundkeeper.load_settings", return_value=Mock(language="auto")),
            patch("soundkeeper.preferred_ui_languages", return_value=[]),
            patch("soundkeeper.check_single_instance", return_value=None),
        ):
            soundkeeper.main()
        self.assertEqual(events, ["config"])
        self.user32.SetProcessDPIAware.assert_called_once_with()

    def test_dpi_initializes_before_any_single_instance_message(self):
        events = []
        with (
            patch(
                "soundkeeper.initialize_dpi_awareness",
                side_effect=lambda: events.append("dpi"),
            ),
            patch(
                "soundkeeper.config_path", side_effect=lambda: events.append("config")
            ),
            patch("soundkeeper.load_settings", return_value=Mock(language="auto")),
            patch("soundkeeper.preferred_ui_languages", return_value=[]),
            patch(
                "soundkeeper.check_single_instance",
                side_effect=lambda language: events.append("mutex"),
            ),
        ):
            soundkeeper.main()
        self.assertEqual(events, ["dpi", "config", "mutex"])


if __name__ == "__main__":
    unittest.main()
