# CyberGhost Status Indicator

GNOME system tray widget that shows the status of the CyberGhost VPN
[Linux CLI](https://www.cyberghostvpn.com/) (`cyberghostvpn` command).

## Features

- **Icon in the top bar** showing the word VPN:
  - **green** = connected
  - **gray** = disconnected
- On click it shows:
  - connection status (VPN ON / VPN OFF)
  - **server** in use (e.g. `berlin-s405-i02`)
  - **public IP** and **location** (city/country)
- Quick actions:
  - **Connect to...** (Italy, Germany, Netherlands, France, Spain, Switzerland, United Kingdom, United States)
  - **Disconnect**
  - **Refresh status**
  - **Quit**
- Desktop notifications when the connection state changes
- **Single instance**: launching it again while running just exits
- **Autostart** at login

Geolocation uses [ipwho.is](https://ipwho.is/) with a fallback to
[ip-api.com](http://ip-api.com/). Lookups made while the VPN is down
(or while switching servers) are discarded to avoid showing a wrong location.

## Requirements

- GNOME with the **AppIndicator / KStatusNotifier** extension enabled
  (Ubuntu: `gnome-shell-extension-appindicator`)
- The CyberGhost CLI client: `cyberghostvpn` (installed and configured with
  `sudo cyberghostvpn --setup`)
- Python 3 + GI packages:
  - `python3-gi`
  - `gir1.2-ayatanaappindicator3-0.1`
  - `gir1.2-pango-1.0`

## Installation

```bash
git clone https://github.com/andreagosto/cyberghost-status-indicator.git
cd cyberghost-status-indicator

# if the GI dependencies are missing:
sudo apt install -y python3-gi gir1.2-ayatanaappindicator3-0.1 gir1.2-pango-1.0

./install.sh
```

The indicator starts immediately and appears in the top bar.
Log out and back in to enable autostart at login (already configured).

### Using from the terminal (without the widget)

```bash
cyberghostvpn --country-code de            # list servers in Germany
sudo cyberghostvpn --country-code de --connect
cyberghostvpn --status
sudo cyberghostvpn --stop
```

## Uninstall

```bash
./uninstall.sh
```

## Customization

- **Countries in the menu**: edit the `POPULAR_COUNTRIES` dict in
  `cyberghost-indicator.py`.
- **Icons**: regenerate them with `python3 make-icons.py` (colors/font are
  editable in the script).

## Debug

Enable logging with `CG_DEBUG=1` (file `/tmp/cg-indicator.log`):

```bash
CG_DEBUG=1 setsid ~/.local/bin/cyberghost-indicator.py &
```
