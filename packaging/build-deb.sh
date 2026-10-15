#!/bin/bash
# Script para empaquetar Hikvision SADP GUI (.deb y .tar.gz)
set -e

RAW_VERSION="${1:-1.0.1}"
VERSION="${RAW_VERSION#v}" # Quitar 'v' si existe
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${2:-$ROOT_DIR}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Construyendo paquetes para Hikvision SADP v$VERSION        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$ROOT_DIR"

# 1. Compilar sadp-linux-amd64 si no está presente
if [ ! -f "$ROOT_DIR/sadp-linux-amd64" ]; then
    echo "➡️ Compilando binario Go sadp-linux-amd64..."
    TEMP_GO_DIR=$(mktemp -d)
    git clone --depth 1 https://github.com/cameronnewman/hikvision-tooling.git "$TEMP_GO_DIR"
    (
        cd "$TEMP_GO_DIR"
        CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o "$ROOT_DIR/sadp-linux-amd64" ./cmd/sadp
    )
    rm -rf "$TEMP_GO_DIR"
    echo "✅ Binario Go compilado con éxito."
fi
chmod +x "$ROOT_DIR/sadp-linux-amd64"

# 2. Preparar directorio temporal para .deb
BUILD_DIR=$(mktemp -d)
PKG_NAME="hikvision-sadp-gui_${VERSION}_amd64"
PKG_DIR="$BUILD_DIR/$PKG_NAME"

echo "➡️ Preparando estructura de archivos Debian..."
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/opt/hikvision-sadp"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/pixmaps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/256x256/apps"

# Copiar archivos del programa
cp "$ROOT_DIR/gui_sadp.py" "$PKG_DIR/opt/hikvision-sadp/"
cp "$ROOT_DIR/sadp_discover.py" "$PKG_DIR/opt/hikvision-sadp/"
cp "$ROOT_DIR/i18n.py" "$PKG_DIR/opt/hikvision-sadp/"
cp "$ROOT_DIR/sadp-linux-amd64" "$PKG_DIR/opt/hikvision-sadp/"

# Copiar lanzador y desktop
cp "$ROOT_DIR/packaging/sadp-gui" "$PKG_DIR/usr/bin/sadp-gui"
cp "$ROOT_DIR/packaging/sadp-gui.desktop" "$PKG_DIR/usr/share/applications/sadp-gui.desktop"

# Copiar iconos
if [ -f "$ROOT_DIR/assets/hikvision-sadp.png" ]; then
    cp "$ROOT_DIR/assets/hikvision-sadp.png" "$PKG_DIR/opt/hikvision-sadp/"
    cp "$ROOT_DIR/assets/hikvision-sadp.png" "$PKG_DIR/usr/share/pixmaps/hikvision-sadp.png"
fi
if [ -f "$ROOT_DIR/assets/hikvision-sadp-128.png" ]; then
    cp "$ROOT_DIR/assets/hikvision-sadp-128.png" "$PKG_DIR/usr/share/icons/hicolor/128x128/apps/hikvision-sadp.png"
fi
if [ -f "$ROOT_DIR/assets/hikvision-sadp-256.png" ]; then
    cp "$ROOT_DIR/assets/hikvision-sadp-256.png" "$PKG_DIR/usr/share/icons/hicolor/256x256/apps/hikvision-sadp.png"
fi

# Generar archivo control con la versión correcta
sed "s/@VERSION@/$VERSION/g" "$ROOT_DIR/packaging/debian/control" > "$PKG_DIR/DEBIAN/control"

# Copiar scripts de mantenimiento debian
cp "$ROOT_DIR/packaging/debian/postinst" "$PKG_DIR/DEBIAN/postinst"
cp "$ROOT_DIR/packaging/debian/prerm" "$PKG_DIR/DEBIAN/prerm"
cp "$ROOT_DIR/packaging/debian/postrm" "$PKG_DIR/DEBIAN/postrm"

# Normalizar saltos de línea y permisos
find "$PKG_DIR/DEBIAN" -type f -exec sed -i 's/\r$//' {} +
find "$PKG_DIR/usr/bin" -type f -exec sed -i 's/\r$//' {} +

chmod 755 "$PKG_DIR/DEBIAN/postinst" "$PKG_DIR/DEBIAN/prerm" "$PKG_DIR/DEBIAN/postrm"
chmod 644 "$PKG_DIR/DEBIAN/control"
chmod 755 "$PKG_DIR/usr/bin/sadp-gui"
chmod 755 "$PKG_DIR/opt/hikvision-sadp/sadp-linux-amd64"
chmod 755 "$PKG_DIR/opt/hikvision-sadp"/*.py
chmod 644 "$PKG_DIR/usr/share/applications/sadp-gui.desktop"

# 3. Construir paquete .deb
echo "➡️ Empaquetando $PKG_NAME.deb..."
dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUTPUT_DIR/${PKG_NAME}.deb"
echo "✅ Paquete Debian creado: $OUTPUT_DIR/${PKG_NAME}.deb"

# 4. Construir paquete portátil .tar.gz
TAR_NAME="hikvision-sadp-gui_${VERSION}_linux_amd64"
TAR_DIR="$BUILD_DIR/$TAR_NAME"
mkdir -p "$TAR_DIR"

echo "➡️ Preparando paquete portátil $TAR_NAME.tar.gz..."
cp "$ROOT_DIR/gui_sadp.py" "$TAR_DIR/"
cp "$ROOT_DIR/sadp_discover.py" "$TAR_DIR/"
cp "$ROOT_DIR/i18n.py" "$TAR_DIR/"
cp "$ROOT_DIR/sadp-linux-amd64" "$TAR_DIR/"
cp "$ROOT_DIR/packaging/sadp-gui" "$TAR_DIR/"
cp "$ROOT_DIR/packaging/sadp-gui.desktop" "$TAR_DIR/"
cp "$ROOT_DIR/packaging/tarball-install.sh" "$TAR_DIR/install.sh"
cp "$ROOT_DIR/packaging/tarball-uninstall.sh" "$TAR_DIR/uninstall.sh"

if [ -f "$ROOT_DIR/assets/hikvision-sadp.png" ]; then
    cp "$ROOT_DIR/assets/hikvision-sadp.png" "$TAR_DIR/"
fi
if [ -f "$ROOT_DIR/README.md" ]; then
    cp "$ROOT_DIR/README.md" "$TAR_DIR/"
fi
if [ -f "$ROOT_DIR/LICENSE" ]; then
    cp "$ROOT_DIR/LICENSE" "$TAR_DIR/"
fi

find "$TAR_DIR" -type f -name "*.sh" -exec sed -i 's/\r$//' {} +
chmod +x "$TAR_DIR"/*.sh "$TAR_DIR/sadp-gui" "$TAR_DIR/sadp-linux-amd64"

tar -czf "$OUTPUT_DIR/${TAR_NAME}.tar.gz" -C "$BUILD_DIR" "$TAR_NAME"
echo "✅ Paquete Tarball creado: $OUTPUT_DIR/${TAR_NAME}.tar.gz"

# Limpieza
rm -rf "$BUILD_DIR"

echo ""
echo "🎉 Paquetes construidos exitosamente en: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR/${PKG_NAME}.deb" "$OUTPUT_DIR/${TAR_NAME}.tar.gz"
