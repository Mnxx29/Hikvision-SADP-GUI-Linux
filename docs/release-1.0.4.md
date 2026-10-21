# 1.0.4 — a visual identity for SADP for Linux

A charcoal and red workspace, a dedicated application header and clearer action hierarchy give the project its own appearance. The camera icon now has a transparent exterior instead of a white square.

Language selection lives in the discreet settings menu (`⋯ → Language / Idioma`). English and Español appear in full, the preference is saved, and changing language does not require restarting.

Qt's desktop identity now matches `sadp-gui.desktop`, so Ubuntu can associate the running window with its launcher and icon under Wayland. The launcher also declares the X11 startup class. Tarball installations now install themed icons and refresh the icon cache, matching the Debian package.

Device discovery and management behavior is unchanged. The hardware validation limits described in the [1.0.3 validation report](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/blob/v1.0.3/docs/validation-1.0.3.md) still apply.

Validation: 40 automated tests passed on Ubuntu, and a real scan returned 35 devices. See the [1.0.4 validation report](https://github.com/Mnxx29/Hikvision-SADP-GUI-Linux/blob/v1.0.4/docs/validation-1.0.4.md) for installation, desktop integration and remaining limits.
