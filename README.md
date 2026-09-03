# CyberGhost Status Indicator

Widget per la barra di sistema di GNOME che mostra lo stato della VPN
[Cli CyberGhost per Linux](https://www.cyberghostvpn.com/) (comando `cyberghostvpn`).

## Funzioni

- **Icona nella barra in alto** con la scritta VPN:
  - **verde** = connesso
  - **grigia** = disconnesso
- Al click mostra:
  - stato connessione (VPN ATTIVA / NON ATTIVA)
  - **server** usato (es. `berlin-s405-i02`)
  - **IP pubblico** e **posizione** (città/paese)
- Menu rapido:
  - **Connetti a...** (Italia, Germania, Paesi Bassi, Francia, Spagna, Svizzera, Regno Unito, Stati Uniti)
  - **Disconnetti**
  - **Aggiorna stato**
  - **Esci**
- Notifiche desktop al cambio di stato
- **Anti-duplicazione**: se è già in esecuzione, un secondo avvio esce subito
- **Avvio automatico** al login

La geolocalizzazione usa [ipwho.is](https://ipwho.is/) con fallback
[ip-api.com](http://ip-api.com/). Le misure prese quando la VPN è spenta
(o durante il cambio server) vengono scartate per evitare posizioni errate.

## Requisiti

- GNOME con estensione **AppIndicator / KStatusNotifier** attiva
  (Ubuntu: `gnome-shell-extension-appindicator`)
- Client CyberGhost CLI: `cyberghostvpn` (installato e configurato con
  `sudo cyberghostvpn --setup`)
- Python 3 + pacchetti GI:
  - `python3-gi`
  - `gir1.2-ayatanaappindicator3-0.1`
  - `gir1.2-pango-1.0`

## Installazione

```bash
git clone https://github.com/andreagosto/cyberghost-status-indicator.git
cd cyberghost-status-indicator

# se mancano le dipendenze GI:
sudo apt install -y python3-gi gir1.2-ayatanaappindicator3-0.1 gir1.2-pango-1.0

./install.sh
```

Al termine l'indicatore parte subito e comparirà nella barra in alto.
Riavvio la sessione se vuoi l'avvio automatico al login (già configurato).

### Uso da terminale (senza widget)

```bash
cyberghostvpn --country-code de            # elenca i server tedeschi
sudo cyberghostvpn --country-code de --connect
cyberghostvpn --status
sudo cyberghostvpn --stop
```

## Disinstallazione

```bash
./uninstall.sh
```

## Personalizzazione

- **Paesi nel menu**: modifica il dizionario `POPULAR_COUNTRIES` in
  `cyberghost-indicator.py`.
- **Icone**: rigenerale con `python3 make-icons.py` (colori/font modificabili
  nello script).

## Debug

Attiva i log con `CG_DEBUG=1` (file `/tmp/cg-indicator.log`):

```bash
CG_DEBUG=1 setsid ~/.local/bin/cyberghost-indicator.py &
```
