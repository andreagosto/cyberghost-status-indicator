#!/bin/bash
# Installs the CyberGhost Status Indicator for the current user.
# Requires the CyberGhost CLI client (cyberghostvpn) to be installed.

set -e

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/cyberghost-indicator"
APP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Checking Python/GI dependencies ..."
if ! python3 -c "import gi; gi.require_version('AyatanaAppIndicator3','0.1')" 2>/dev/null; then
    echo "Missing gir1.2-ayatanaappindicator3-0.1 (or the python3-gi package)."
    echo "Install with:"
    echo "    sudo apt install -y gir1.2-ayatanaappindicator3-0.1 python3-gi gir1.2-pango-1.0"
    exit 1
fi

if ! command -v cyberghostvpn >/dev/null 2>&1; then
    echo "WARNING: 'cyberghostvpn' not found in PATH."
    echo "This indicator only works with the CyberGhost CLI client installed."
fi

mkdir -p "$BIN_DIR" "$ICON_DIR" "$APP_DIR" "$AUTOSTART_DIR"

echo "==> Copying the script ..."
cp "$SRC_DIR/cyberghost-indicator.py" "$BIN_DIR/"
chmod +x "$BIN_DIR/cyberghost-indicator.py"

echo "==> Copying the icons ..."
cp "$SRC_DIR"/icons/vpn-on.png "$SRC_DIR"/icons/vpn-off.png "$ICON_DIR/"

echo "==> Creating desktop entries ..."
cat > "$AUTOSTART_DIR/cyberghost-indicator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CyberGhost Indicator
Comment=Shows the CyberGhost VPN status
Exec=$BIN_DIR/cyberghost-indicator.py
X-GNOME-Autostart-enabled=true
Terminal=false
EOF

cat > "$APP_DIR/cyberghost-indicator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CyberGhost Indicator
Comment=Shows the CyberGhost VPN status in the system tray
Exec=$BIN_DIR/cyberghost-indicator.py
Icon=$ICON_DIR/vpn-on.png
Terminal=false
Categories=Network;GNOME;
X-GNOME-Autostart-enabled=false
StartupNotify=false
EOF

update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true

echo "==> Starting the indicator ..."
if ! pgrep -f 'cyberghost-indicator[.]py' >/dev/null 2>&1; then
    setsid "$BIN_DIR/cyberghost-indicator.py" >/dev/null 2>&1 < /dev/null &
    disown 2>/dev/null || true
    echo "Indicator started."
else
    echo "Indicator is already running."
fi

echo
echo "Done. Look for 'CyberGhost Indicator' in the Applications menu,"
echo "or log out and back in to enable autostart."
