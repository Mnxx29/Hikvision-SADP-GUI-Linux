#!/bin/bash
# Debian/Ubuntu source installation uses the same package and permission model.
set -euo pipefail
[ "$EUID" -ne 0 ] || { echo 'Run as your normal user: bash setup-produccion.sh' >&2; exit 1; }
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo apt-get update
sudo apt-get install -y python3 python3-pyqt6 git golang-go dpkg-dev
bash "$ROOT_DIR/packaging/build-deb.sh"
VERSION="$(cat "$ROOT_DIR/VERSION")"
sudo apt-get install -y "$ROOT_DIR/dist/hikvision-sadp-gui_${VERSION}_amd64.deb"
# Retire the older per-user launchers, which otherwise shadow /usr/bin/sadp-gui.
rm -f -- "$HOME/.local/bin/sadp-gui" "$HOME/.local/share/applications/sadp-gui.desktop"
echo 'Installed. Run sadp-gui without sudo.'
