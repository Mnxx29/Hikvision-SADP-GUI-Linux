#!/bin/bash
# Script de desinstalación para la versión tarball
set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Por favor ejecuta como root: sudo bash uninstall.sh"
    exit 1
fi

echo "🗑️ Desinstalando Hikvision SADP GUI..."

rm -rf /opt/hikvision-sadp
rm -f /usr/local/bin/sadp-gui
rm -f /usr/share/applications/sadp-gui.desktop
rm -f /usr/share/pixmaps/hikvision-sadp.png
rm -f /etc/sudoers.d/sadp-gui-routing

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications >/dev/null 2>&1 || true
fi

echo "✅ Desinstalación completada."
