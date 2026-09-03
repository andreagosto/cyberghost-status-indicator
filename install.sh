#!/bin/bash
# Installa il CyberGhost Status Indicator per l'utente corrente.
# Richiede il client CyberGhost CLI installato (cyberghostvpn).

set -e

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/cyberghost-indicator"
APP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Verifica dipendenze Python/GI ..."
if ! python3 -c "import gi; gi.require_version('AyatanaAppIndicator3','0.1')" 2>/dev/null; then
    echo "Manca gir1.2-ayatanaappindicator3-0.1 (o il pacchetto python3-gi)."
    echo "Installa con:"
    echo "    sudo apt install -y gir1.2-ayatanaappindicator3-0.1 python3-gi gir1.2-pango-1.0"
    exit 1
fi

if ! command -v cyberghostvpn >/dev/null 2>&1; then
    echo "ATTENZIONE: 'cyberghostvpn' non trovato nel PATH."
    echo "Questo indicatore funziona SOLO con il client CLI CyberGhost installato."
fi

mkdir -p "$BIN_DIR" "$ICON_DIR" "$APP_DIR" "$AUTOSTART_DIR"

echo "==> Copio lo script ..."
cp "$SRC_DIR/cyberghost-indicator.py" "$BIN_DIR/"
chmod +x "$BIN_DIR/cyberghost-indicator.py"

echo "==> Copio le icone ..."
cp "$SRC_DIR"/icons/vpn-on.png "$SRC_DIR"/icons/vpn-off.png "$ICON_DIR/"

echo "==> Creo le voci desktop ..."
cat > "$AUTOSTART_DIR/cyberghost-indicator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CyberGhost Indicator
Comment=Mostra lo stato della VPN CyberGhost
Exec=$BIN_DIR/cyberghost-indicator.py
X-GNOME-Autostart-enabled=true
Terminal=false
EOF

cat > "$APP_DIR/cyberghost-indicator.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=CyberGhost Indicatore
Comment=Mostra lo stato della VPN CyberGhost nella barra di sistema
Exec=$BIN_DIR/cyberghost-indicator.py
Icon=$ICON_DIR/vpn-on.png
Terminal=false
Categories=Network;GNOME;
X-GNOME-Autostart-enabled=false
StartupNotify=false
EOF

update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true

echo "==> Avvio l'indicatore ..."
if ! pgrep -f 'cyberghost-indicator[.]py' >/dev/null 2>&1; then
    setsid "$BIN_DIR/cyberghost-indicator.py" >/dev/null 2>&1 < /dev/null &
    disown 2>/dev/null || true
    echo "Indicatore avviato."
else
    echo "Indicatore gia' in esecuzione."
fi

echo
echo "Fatto. Cerca 'CyberGhost Indicatore' nel menu Applicazioni,"
echo "oppure riavvia la sessione per l'avvio automatico al login."
