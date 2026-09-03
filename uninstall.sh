#!/bin/bash
# Rimuove il CyberGhost Status Indicator per l'utente corrente.

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/cyberghost-indicator"
APP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "==> Fermo l'indicatore ..."
pkill -f 'cyberghost-indicator[.]py' 2>/dev/null || true

echo "==> Rimuovo i file ..."
rm -f "$BIN_DIR/cyberghost-indicator.py"
rm -rf "$ICON_DIR"
rm -f "$APP_DIR/cyberghost-indicator.desktop"
rm -f "$AUTOSTART_DIR/cyberghost-indicator.desktop"

update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
echo "Disinstallazione completata."
