#!/bin/bash
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo 'Run: sudo bash uninstall.sh' >&2; exit 1; }
if command -v dpkg-query >/dev/null && dpkg-query -W -f='${Status}' hikvision-sadp-gui 2>/dev/null | grep -q 'install ok installed'; then
    echo 'Use sudo apt remove hikvision-sadp-gui for a Debian installation.' >&2
    exit 1
fi
if [ -f /opt/hikvision-sadp/network_setup.py ]; then
    python3 /opt/hikvision-sadp/network_setup.py remove
fi
rm -rf -- /opt/hikvision-sadp
rm -f -- /usr/local/bin/sadp-gui /usr/share/applications/sadp-gui.desktop /usr/share/pixmaps/hikvision-sadp.png /etc/sudoers.d/sadp-gui-routing
if command -v update-desktop-database >/dev/null; then update-desktop-database -q /usr/share/applications; fi
echo 'SADP removed.'
