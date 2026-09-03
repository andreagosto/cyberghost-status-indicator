#!/bin/bash
# Removes the CyberGhost Status Indicator for the current user.

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/cyberghost-indicator"
APP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "==> Stopping the indicator ..."
pkill -f 'cyberghost-indicator[.]py' 2>/dev/null || true

echo "==> Removing files ..."
rm -f "$BIN_DIR/cyberghost-indicator.py"
rm -rf "$ICON_DIR"
rm -f "$APP_DIR/cyberghost-indicator.desktop"
rm -f "$AUTOSTART_DIR/cyberghost-indicator.desktop"

update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
echo "Uninstall complete."
