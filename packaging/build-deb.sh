#!/bin/bash
set -euo pipefail
umask 022
export LC_ALL=C
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT_DIR" show -s --format=%ct HEAD)}"
RAW_VERSION="${1:-$(cat "$ROOT_DIR/VERSION")}"
VERSION="${RAW_VERSION#v}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo 'Expected a version such as 1.0.3' >&2; exit 1; }
OUTPUT_DIR="${2:-$ROOT_DIR/dist}"
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
BUILD_DIR=$(mktemp -d)
trap 'rm -rf -- "$BUILD_DIR"' EXIT
bash "$ROOT_DIR/packaging/build-helper.sh" "$BUILD_DIR/helper"
PKG_NAME="hikvision-sadp-gui_${VERSION}_amd64"
PKG_DIR="$BUILD_DIR/$PKG_NAME"
APP_DIR="$PKG_DIR/opt/hikvision-sadp"
mkdir -p "$PKG_DIR/DEBIAN" "$APP_DIR" "$PKG_DIR/usr/bin" "$PKG_DIR/usr/share/applications" "$PKG_DIR/usr/share/doc/hikvision-sadp-gui"
for module in gui_sadp.py sadp_discover.py sadp_operations.py network_setup.py i18n.py; do
    install -m 644 "$ROOT_DIR/$module" "$APP_DIR/"
done
install -m 755 "$BUILD_DIR/helper/sadp-linux-amd64" "$APP_DIR/"
install -m 644 "$BUILD_DIR/helper/BUILD-INFO.txt" "$APP_DIR/"
install -m 644 "$ROOT_DIR/LICENSE" "$BUILD_DIR/helper/HIKVISION-TOOLING-LICENSE" "$ROOT_DIR/CHANGELOG.md" "$PKG_DIR/usr/share/doc/hikvision-sadp-gui/"
install -m 755 "$ROOT_DIR/packaging/sadp-gui" "$PKG_DIR/usr/bin/"
install -m 644 "$ROOT_DIR/packaging/sadp-gui.desktop" "$PKG_DIR/usr/share/applications/"
install -m 644 "$ROOT_DIR/assets/hikvision-sadp.png" "$APP_DIR/"
for size in 128 256; do
    ICON_DIR="$PKG_DIR/usr/share/icons/hicolor/${size}x${size}/apps"
    mkdir -p "$ICON_DIR"
    install -m 644 "$ROOT_DIR/assets/hikvision-sadp-$size.png" "$ICON_DIR/hikvision-sadp.png"
done
mkdir -p "$PKG_DIR/usr/share/pixmaps"
install -m 644 "$ROOT_DIR/assets/hikvision-sadp.png" "$PKG_DIR/usr/share/pixmaps/"
sed "s/@VERSION@/$VERSION/g" "$ROOT_DIR/packaging/debian/control" > "$PKG_DIR/DEBIAN/control"
for script in postinst prerm postrm; do
    install -m 755 "$ROOT_DIR/packaging/debian/$script" "$PKG_DIR/DEBIAN/"
done
find "$PKG_DIR/DEBIAN" "$PKG_DIR/usr/bin" -type f -exec sed -i 's/\r$//' {} +
(cd "$PKG_DIR" && find opt usr -type f -print0 | sort -z | xargs -0 md5sum > DEBIAN/md5sums)
dpkg-deb --build --root-owner-group "$PKG_DIR" "$OUTPUT_DIR/$PKG_NAME.deb"
TAR_NAME="hikvision-sadp-gui_${VERSION}_linux_amd64"
TAR_DIR="$BUILD_DIR/$TAR_NAME"
mkdir -p "$TAR_DIR"
cp "$APP_DIR/"* "$TAR_DIR/"
cp "$ROOT_DIR/packaging/sadp-gui" "$ROOT_DIR/packaging/sadp-gui.desktop" "$TAR_DIR/"
for size in 128 256; do
    install -m 644 "$ROOT_DIR/assets/hikvision-sadp-$size.png" "$TAR_DIR/"
done
install -m 755 "$ROOT_DIR/packaging/tarball-install.sh" "$TAR_DIR/install.sh"
install -m 755 "$ROOT_DIR/packaging/tarball-uninstall.sh" "$TAR_DIR/uninstall.sh"
cp "$ROOT_DIR/LICENSE" "$ROOT_DIR/README.md" "$ROOT_DIR/README_es.md" "$ROOT_DIR/CHANGELOG.md" "$BUILD_DIR/helper/HIKVISION-TOOLING-LICENSE" "$TAR_DIR/"
find "$TAR_DIR" -type f \( -name '*.sh' -o -name 'sadp-gui' \) -exec sed -i 's/\r$//' {} +
chmod 755 "$TAR_DIR/sadp-gui"
tar --sort=name --mtime="@$SOURCE_DATE_EPOCH" --owner=0 --group=0 --numeric-owner -czf "$OUTPUT_DIR/$TAR_NAME.tar.gz" -C "$BUILD_DIR" "$TAR_NAME"
(cd "$OUTPUT_DIR" && sha256sum "$PKG_NAME.deb" "$TAR_NAME.tar.gz" > SHA256SUMS.txt)
printf 'Packages and checksums: %s\n' "$OUTPUT_DIR"
