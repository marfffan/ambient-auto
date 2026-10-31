#!/bin/sh
# Собирает .deb из исходников: ./build-deb.sh
# Результат: build/ambient-auto_<версия>_all.deb
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
VERSION=$(cat "$ROOT/VERSION")
NAME=ambient-auto
BUILD="$ROOT/build"
PKG="$BUILD/pkg"
DEB="$BUILD/${NAME}_${VERSION}_all.deb"

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "Ошибка: нужен dpkg-deb (пакет dpkg-dev)." >&2
    exit 1
fi

rm -rf "$BUILD"
install -d "$PKG/DEBIAN" \
           "$PKG/usr/lib/$NAME" \
           "$PKG/usr/bin" \
           "$PKG/usr/lib/systemd/system" \
           "$PKG/usr/share/$NAME" \
           "$PKG/usr/share/applications" \
           "$PKG/usr/share/icons/hicolor/scalable/apps" \
           "$PKG/usr/share/doc/$NAME"

install -m755 "$ROOT/src/$NAME"                 "$PKG/usr/lib/$NAME/$NAME"
install -m644 "$ROOT/src/gui.py"                "$PKG/usr/lib/$NAME/gui.py"
install -m755 "$ROOT/src/$NAME-gui"             "$PKG/usr/bin/$NAME-gui"
install -m644 "$ROOT/systemd/$NAME.service"     "$PKG/usr/lib/systemd/system/$NAME.service"
install -m644 "$ROOT/share/config.default.json" "$PKG/usr/share/$NAME/config.default.json"
install -m644 "$ROOT/share/$NAME.desktop"       "$PKG/usr/share/applications/$NAME.desktop"
install -m644 "$ROOT/share/icons/$NAME.svg"     "$PKG/usr/share/icons/hicolor/scalable/apps/$NAME.svg"
install -m644 "$ROOT/README.md"                 "$PKG/usr/share/doc/$NAME/README.md"
install -m644 "$ROOT/packaging/copyright"       "$PKG/usr/share/doc/$NAME/copyright"

for script in postinst prerm postrm; do
    install -m755 "$ROOT/packaging/DEBIAN/$script" "$PKG/DEBIAN/$script"
done

# Проверяем синтаксис Python до упаковки.
python3 -m py_compile "$PKG/usr/lib/$NAME/$NAME" "$PKG/usr/lib/$NAME/gui.py"
find "$PKG" -name __pycache__ -type d -prune -exec rm -rf {} +

INSTALLED_SIZE=$(du -sk "$PKG/usr" | cut -f1)
sed -e "s/@VERSION@/$VERSION/" -e "s/@SIZE@/$INSTALLED_SIZE/" \
    "$ROOT/packaging/DEBIAN/control" > "$PKG/DEBIAN/control"
chmod 644 "$PKG/DEBIAN/control"

dpkg-deb --build --root-owner-group "$PKG" "$DEB"
echo "Готово: $DEB"
