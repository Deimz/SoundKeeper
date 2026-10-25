# DPI awareness validation

## Purpose

SoundKeeper already uses pystray's native Win32 menu backend. This patch adds an
explicit DPI policy instead of replacing the menu implementation or drawing text.
The packaged app requests Per-Monitor V2 through its manifest; direct source runs
initialize DPI before creating UI. Existing host policies are preserved.

No audio, JSON, menu-command, or dependency changes are included in the DPI patch.
Older API fallbacks are covered with mocks, not with real older Windows systems.

## Automated checks

Run from the repository root after installing the requirements:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/SyncReadme.py --check
```

The suite contains the existing 21 regression tests and nine DPI tests covering
PMv2 success, unavailable/unsupported APIs, legacy fallbacks, existing host policy,
nonfatal failure, and initialization before single-instance message boxes.

An independent build avoids replacing a running or previously released binary:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist/dpi-preview --workpath build/dpi-preview SoundKeeper.spec
```

Inspect the resulting executable's embedded manifest, not only the source XML.
It must contain `PerMonitorV2,PerMonitor`, `true/pm`, normal-user execution,
Common Controls v6, Windows compatibility entries, and long-path support.
The direct CLI build in both README guides must use the same manifest.

## Results on the development machine

- All 30 unit tests passed; Ruff E/F/I, formatting, and whitespace checks passed.
- The spec build's embedded manifest contains the required declarations.
- The direct CLI build also succeeded in an isolated output/spec directory; its
  embedded manifest is identical to the spec build's. When relocating the generated
  spec with `--specpath`, use absolute manifest/icon paths because PyInstaller
  resolves these resources relative to the spec directory.
- The spec-built executable is 29,546,386 bytes (28.18 MiB), an increase of
  1,153 bytes over the preceding configurable build on the same machine.
- A separate source-run test instance used the actual SoundKeeper class and DPI
  initializer, a temporary project-local configuration, and mocked audio. Its tray
  window and menu-owner window both reported Per-Monitor V2 and 144 DPI (150%).
- The existing application remained running and its preferences and startup
  registration were not changed. Full startup of the production executable was
  not tested concurrently because the existing instance holds the single-instance
  mutex; manifest inspection and source-window checks are separate evidence.
- Desktop capture/control was denied by the desktop tool. Pixel-level comparisons
  and the native interaction checklist below are **not yet verified**.

These results describe one machine and dependency set, not all Windows versions.

## Manual acceptance checklist

Exit an older SoundKeeper normally before starting the new production executable.
Do not change Windows compatibility DPI overrides while comparing builds.

- At 150%, compare text edges with AKKO on the same display. Check submenus,
  checked/radio items, disabled custom timings, and long translated labels.
- Open and dismiss repeatedly with Escape and outside clicks. Exercise submenus,
  language changes, activation, and normal exit without changing autostart.
- Confirm the production tray window's actual context is PMv2, rather than relying
  solely on the manifest. A host or compatibility override can affect the result.
- Check 100%, 125%, and 200% when available; these scales were not tested here.
- On mixed-DPI displays, check menu placement and size on each monitor. This was
  not tested here. pystray creates hidden owner windows at the origin; this patch
  does not introduce a private-backend workaround or claim full mixed-DPI support.

If a cross-monitor defect reproduces, record the monitor layout, scale factors,
menu position, and owner-window DPI for a separate follow-up patch.

## Suggested independent commit

`Fix Windows tray DPI awareness without changing the menu backend`

Keep previously prepared bilingual-documentation changes separate when staging
this patch. Update the two standalone guides and regenerate the homepage together.
Do not commit virtual environments, temporary test harnesses, or built executables.
