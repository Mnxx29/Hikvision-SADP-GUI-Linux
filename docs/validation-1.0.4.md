# Validation — 1.0.4

VM test date: **2026-10-21**. Ubuntu Desktop 24.04 amd64 in the existing VirtualBox test VM. These results describe the local validation performed before publication. GitHub Actions records the tests and release build from the tagged source commit separately in the repository's Actions history.

- All **40 tests passed** on Ubuntu, including Qt worker tests, language switching and persistence, translated button widths, horizontal table scrolling beside the network panel, desktop identity, matching translation keys and PNG transparency.
- A real scan using the installed application returned **35 devices** under Wayland. No device configuration or binding was changed.
- The Debian package upgraded the installed 1.0.3 to 1.0.4 successfully. `dpkg --verify hikvision-sadp-gui` found no mismatches, and the five installed runtime modules matched the tested source bytes.
- The window advertised `sadp-gui` as its desktop identity under Wayland. A separate X11 run reported `WM_CLASS = "check_x11.py", "sadp-gui"`, matching the launcher's `StartupWMClass`.
- Visual inspection of the running Ubuntu desktop confirmed the application icon appears in the dock without the old white exterior. The English and Español menu labels were visible in full. English/Spanish window captures and the Spanish network panel were saved for review.
- The Debian desktop entry passed `desktop-file-validate` without errors. Its existing `Network;Utility;` category combination produces a nonfatal hint about appearing in more than one menu category.
- Shell syntax checks passed. Both installer formats were built, and both themed icon files in the tarball matched the source assets. Tarball install/uninstall was not replayed during this visual update; the added icon install/remove commands were checked in the archive and scripts.

Local packages, checksums, screenshots and raw logs are kept in the ignored `dist/v1.0.4/` directory. The VM preview imports the installed `/opt/hikvision-sadp` modules and performs the normal scan. Published assets are rebuilt by GitHub Actions from the tagged source and include their own `SHA256SUMS.txt`; archive timestamps and documentation can differ from pre-commit local builds.

The [1.0.3 hardware validation limits](validation-1.0.3.md) still apply. This update does not establish compatibility for real device network changes or unbind operations. The base Ubuntu snapshot was not modified.
