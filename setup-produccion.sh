#!/bin/bash

# SADP GUI para Linux - Script de Instalación de Producción (Versión Definitiva)
# Uso: bash setup-produccion.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    SADP GUI para Linux - Instalación de Producción        ║"
echo "║    Descubridor de Cámaras Hikvision                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [[ "$EUID" -eq 0 ]]; then
    echo "❌ ERROR: No ejecutar como root/sudo."
    echo "   Uso: bash setup-produccion.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin/sadp"
mkdir -p "$INSTALL_DIR"

echo "📋 Sistema: $(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2 || uname -a)"
echo "📁 Destino: $INSTALL_DIR"
echo ""

# FUNCIÓN: Configurar firewall base
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
configure_ufw() {
    echo "🔐 Configurando UFW..."
    if command -v ufw &> /dev/null; then
        echo "   • Permitir UDP 37020 in..."
        sudo ufw allow 37020/udp 2>/dev/null || true
        
        echo "   • Permitir respuestas UDP desde puerto 37020..."
        sudo ufw allow from any port 37020 proto udp 2>/dev/null || true
        
        echo "   • Permitir multicast 224.0.0.0/4 out..."
        sudo ufw allow out proto udp to 224.0.0.0/4 2>/dev/null || true
        
        if ! sudo ufw status | grep -q "Status: active"; then
            echo "   • Habilitando UFW..."
            sudo ufw --force enable 2>/dev/null || true
        fi
        echo "   ✅ UFW configurado."
    else
        echo "   ⚠️ UFW no detectado, omitiendo."
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 1: Instalación de dependencias
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/6] Instalando dependencias del sistema..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "➡️ [1.1] Ejecutando apt update..."
sudo apt update || true
echo ""

echo "➡️ [1.2] Instalando paquetes (python3, python3-pyqt6, golang-go, git, ufw, libcap2-bin)..."
sudo apt install -y python3 python3-pyqt6 golang-go git ufw libcap2-bin

GO_VERSION=$(go version 2>/dev/null | grep -oP 'go\K[0-9]+\.[0-9]+' | head -1 || echo "ok")
echo "✅ Dependencias instaladas (Go $GO_VERSION)."
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 2: Compilar binario SADP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/6] Compilando binario SADP en Go..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TEMP_BUILD="/tmp/sadp-build-$$"
echo "➡️ [2.1] Creando directorio temporal: $TEMP_BUILD"
mkdir -p "$TEMP_BUILD"
cd "$TEMP_BUILD"

echo "➡️ [2.2] Clonando hikvision-tooling..."
git clone --depth 1 https://github.com/cameronnewman/hikvision-tooling.git
cd hikvision-tooling

echo "➡️ [2.3] Compilando sadp-linux-amd64..."
if CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o sadp-linux-amd64 ./cmd/sadp; then
    echo "➡️ [2.4] Copiando binario a $INSTALL_DIR/"
    cp sadp-linux-amd64 "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/sadp-linux-amd64"
    echo "✅ Binario Go instalado."
else
    echo "❌ Error al compilar binario Go."
    rm -rf "$TEMP_BUILD"
    exit 1
fi
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 3: Copiar GUI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/6] Copiando archivos de la interfaz..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ -f "$SCRIPT_DIR/gui_sadp.py" ]]; then
    echo "➡️ [3.1] Copiando gui_sadp.py..."
    cp "$SCRIPT_DIR/gui_sadp.py" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/gui_sadp.py"
    
    if [[ -f "$SCRIPT_DIR/sadp_discover.py" ]]; then
        echo "➡️ [3.2] Copiando sadp_discover.py..."
        cp "$SCRIPT_DIR/sadp_discover.py" "$INSTALL_DIR/"
    fi
    
    if [[ -f "$SCRIPT_DIR/i18n.py" ]]; then
        echo "➡️ [3.3] Copiando i18n.py..."
        cp "$SCRIPT_DIR/i18n.py" "$INSTALL_DIR/"
    fi
    echo "✅ Archivos Python instalados."
else
    echo "❌ Error: gui_sadp.py no encontrado."
    exit 1
fi
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 4: Configurar permisos silenciosos
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/6] Configurando sudoers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SUDOERS_FILE="/etc/sudoers.d/sadp-gui-routing"
echo "➡️ [4.1] Escribiendo $SUDOERS_FILE..."
echo "ALL ALL=(root) NOPASSWD: /usr/sbin/ip route add 239.255.255.250/32 *, /usr/sbin/ip route change 239.255.255.250/32 *, /bin/ip route add 239.255.255.250/32 *, /bin/ip route change 239.255.255.250/32 *, /usr/sbin/ufw allow in on *, /sbin/sysctl *, /usr/sbin/sysctl *" | sudo tee "$SUDOERS_FILE" >/dev/null

echo "➡️ [4.2] Aplicando chmod 0440..."
sudo chmod 0440 "$SUDOERS_FILE"
echo "✅ Reglas sudoers configuradas."
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 5: Crear Lanzador Inteligente Multi-Interfaz
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/6] Creando lanzador y acceso directo..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LAUNCHER="$HOME/.local/bin/sadp-gui"

echo "➡️ [5.1] Generando script $LAUNCHER..."
cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/bin/bash
# 1. Configurar rp_filter=2 (modo laxo) para permitir recibir respuestas UDP de subredes distintas
sudo sysctl -w net.ipv4.conf.all.rp_filter=2 >/dev/null 2>&1 || true
sudo sysctl -w net.ipv4.conf.default.rp_filter=2 >/dev/null 2>&1 || true

# 2. Detectar TODAS las interfaces de red activas (Ethernet, WiFi, USB, VLANs, etc.)
IFACES=$(ip -o link show | awk -F': ' '$2 !~ /^lo/ && $3 ~ /state (UP|UNKNOWN)/ {print $2}' | cut -d'@' -f1)

# 3. Forzar ruta multicast y abrir firewall en CADA interfaz activa
for IFACE in $IFACES; do
    [ -z "$IFACE" ] && continue
    sudo ip route add 239.255.255.250/32 dev "$IFACE" 2>/dev/null || \
    sudo ip route change 239.255.255.250/32 dev "$IFACE" 2>/dev/null || true
    
    sudo ufw allow in on "$IFACE" to any port 37020 proto udp 2>/dev/null || true
done

# 4. Garantizar que las respuestas SADP no sean bloqueadas por UFW
sudo ufw allow from any port 37020 proto udp 2>/dev/null || true

# 5. Iniciar GUI
cd "$HOME/.local/bin/sadp"
python3 gui_sadp.py
LAUNCHER_EOF

chmod +x "$LAUNCHER"

APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"
DESKTOP_FILE="$APPLICATIONS_DIR/sadp-gui.desktop"

echo "➡️ [5.2] Generando $DESKTOP_FILE..."
cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SADP GUI
Comment=Descubrir cámaras Hikvision en la red local
Exec=$LAUNCHER
Terminal=false
Icon=network-workgroup
Categories=Network;Utility;
StartupNotify=true
DESKTOP_EOF
chmod +x "$DESKTOP_FILE"
echo "✅ Lanzador y desktop file creados."
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Paso 6: Configurar firewall inicial y setcap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[6/6] Permisos de red y limpieza..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
configure_ufw

if command -v setcap &> /dev/null; then
    echo "➡️ Asignando cap_net_raw a sadp-linux-amd64..."
    sudo setcap cap_net_raw=ep "$INSTALL_DIR/sadp-linux-amd64" 2>/dev/null || true
fi

echo "➡️ Limpiando $TEMP_BUILD..."
rm -rf "$TEMP_BUILD"
echo "✅ Instalación finalizada."
echo ""