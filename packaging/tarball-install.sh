#!/bin/bash
# Script de instalación portátil (para distribuciones basadas en tar.gz)
set -e

if [ "$EUID" -ne 0 ]; then
    echo "❌ Por favor ejecuta como root: sudo bash install.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/hikvision-sadp"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Instalando Hikvision SADP GUI para Linux                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Crear directorios
mkdir -p "$INSTALL_DIR"
mkdir -p /usr/local/bin
mkdir -p /usr/share/applications
mkdir -p /usr/share/pixmaps

# 2. Copiar archivos de la aplicación
echo "➡️ Copiando archivos a $INSTALL_DIR..."
cp "$SCRIPT_DIR/gui_sadp.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/sadp_discover.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/i18n.py" "$INSTALL_DIR/"
if [ -f "$SCRIPT_DIR/sadp-linux-amd64" ]; then
    cp "$SCRIPT_DIR/sadp-linux-amd64" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/sadp-linux-amd64"
    if command -v setcap >/dev/null 2>&1; then
        setcap cap_net_raw=ep "$INSTALL_DIR/sadp-linux-amd64" 2>/dev/null || true
    fi
fi
if [ -f "$SCRIPT_DIR/hikvision-sadp.png" ]; then
    cp "$SCRIPT_DIR/hikvision-sadp.png" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/hikvision-sadp.png" "/usr/share/pixmaps/"
fi

# 3. Copiar lanzador
echo "➡️ Instalando comando sadp-gui en /usr/local/bin/..."
cp "$SCRIPT_DIR/sadp-gui" /usr/local/bin/sadp-gui
chmod +x /usr/local/bin/sadp-gui

# 4. Copiar Desktop Entry
echo "➡️ Instalando acceso directo en el menú de aplicaciones..."
cp "$SCRIPT_DIR/sadp-gui.desktop" /usr/share/applications/
chmod 644 /usr/share/applications/sadp-gui.desktop

# 5. Configurar sudoers para ruteo multicast
echo "➡️ Configurando reglas sudoers en /etc/sudoers.d/sadp-gui-routing..."
SUDOERS_FILE="/etc/sudoers.d/sadp-gui-routing"
cat > "$SUDOERS_FILE" << 'EOF'
ALL ALL=(root) NOPASSWD: /usr/sbin/ip route add 239.255.255.250/32 *, /usr/sbin/ip route change 239.255.255.250/32 *, /bin/ip route add 239.255.255.250/32 *, /bin/ip route change 239.255.255.250/32 *, /usr/sbin/ufw allow in on *, /usr/sbin/ufw allow from any port 37020 proto udp, /sbin/sysctl *, /usr/sbin/sysctl *
EOF
chmod 0440 "$SUDOERS_FILE"

# 6. Configurar UFW si existe
if command -v ufw >/dev/null 2>&1; then
    echo "➡️ Configurando reglas UFW..."
    ufw allow 37020/udp >/dev/null 2>&1 || true
    ufw allow from any port 37020 proto udp >/dev/null 2>&1 || true
    ufw allow out proto udp to 224.0.0.0/4 >/dev/null 2>&1 || true
fi

# 7. Actualizar base de datos de escritorio
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications >/dev/null 2>&1 || true
fi

echo ""
echo "✅ Instalación completada exitosamente."
echo "   Puedes iniciar la herramienta escribiendo 'sadp-gui' en tu terminal o"
echo "   buscando 'Hikvision SADP' en tu menú de aplicaciones."
echo ""
