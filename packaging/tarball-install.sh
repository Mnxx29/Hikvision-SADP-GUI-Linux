#!/bin/bash
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo 'Run: sudo bash install.sh' >&2; exit 1; }
if command -v dpkg-query >/dev/null && dpkg-query -W -f='${Status}' hikvision-sadp-gui 2>/dev/null | grep -q 'install ok installed'; then
    echo 'A Debian package is already installed. Use apt to upgrade it.' >&2
    exit 1
fi
python3 -c 'import sys; assert sys.version_info >= (3, 9); import PyQt6.QtWidgets; from PyQt6.QtCore import PYQT_VERSION; assert PYQT_VERSION >= 0x060400' || { echo 'Install Python >=3.9 and PyQt6 >=6.4 using your distribution package manager.' >&2; exit 1; }
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR=/opt/hikvision-sadp
mkdir -p "$INSTALL_DIR" /usr/local/bin /usr/share/applications /usr/share/pixmaps
for file in gui_sadp.py sadp_discover.py sadp_operations.py network_setup.py i18n.py BUILD-INFO.txt LICENSE HIKVISION-TOOLING-LICENSE; do
    install -m 644 "$SCRIPT_DIR/$file" "$INSTALL_DIR/"
done
install -m 755 "$SCRIPT_DIR/sadp-linux-amd64" "$INSTALL_DIR/"
install -m 644 "$SCRIPT_DIR/hikvision-sadp.png" "$INSTALL_DIR/"
install -m 644 "$SCRIPT_DIR/hikvision-sadp.png" /usr/share/pixmaps/
for size in 128 256; do
    ICON_DIR="/usr/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "$ICON_DIR"
    install -m 644 "$SCRIPT_DIR/hikvision-sadp-$size.png" "$ICON_DIR/hikvision-sadp.png"
done
python3 "$INSTALL_DIR/network_setup.py" configure
install -m 755 "$SCRIPT_DIR/sadp-gui" /usr/local/bin/sadp-gui
install -m 644 "$SCRIPT_DIR/sadp-gui.desktop" /usr/share/applications/
if command -v update-desktop-database >/dev/null; then update-desktop-database -q /usr/share/applications; fi
if command -v gtk-update-icon-cache >/dev/null; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi
echo 'Installed. Start sadp-gui as your normal user.'
