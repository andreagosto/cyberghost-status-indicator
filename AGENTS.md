# AGENTS.md

## Progetto
CyberGhost Status Indicator — widget GNOME (top bar) che mostra lo stato del VPN CyberGhost
tramite la CLI `cyberghostvpn`.

## Contesto: Helmer

Questa cartella **è** il progetto omonimo — `cyberghost-status-indicator` — e non un pezzo di un altro:
il nome del progetto è il nome della cartella.

Vive in **Helmer**, la board locale dei lavori assistiti dall'IA, in un contesto di
orchestrazione leggera: Helmer non decide al posto tuo, ma fa da quadro (ti ha
creato la cartella, sa quali todo hai, sa quali altri progetti esistono) e mette in
contatto i progetti fra loro. Attraverso gli MCP puoi quindi **invocare gli altri
progetti e essere invocato**:

- `facetoface_consult(project, question)` — chiedi o avvisa un altro progetto: è una
  sessione dedicata per progetto, con il suo contesto. Usalo quando la risposta sta
  altrove, invece di inventarla; `facetoface_list_projects` elenca i vicini.
- `helmer_todo_*` (`todo_list`, `todo_create`, `todo_set_done`, `todo_set_blocked`) —
  i todo di **questo** progetto: sono lavoro da fare qui, **non** messaggi verso altri
  progetti (per quelli c'è `facetoface_consult`).
- **Vale anche il contrario**: un altro progetto, o l'utente da Helmer, può chiamare
  te con una domanda via `facetoface_consult`. Rispondi col contesto di questa
  cartella e non dare per scontato che chi chiede sappia cosa c'è qui.

**Confine fra progetti — regola tassativa.** Lavori qui, e solo qui: gli altri
progetti **non sono tuoi**. Fuori da questa cartella non modifichi, crei, sposti o
cancelli file, non fai commit e non lanci comandi che cambiano stato, a meno che
l'utente non te lo chieda **esplicitamente** in questa conversazione (dicendo quale
progetto e quale modifica). Se dalla conversazione emerge una modifica a un **altro**
progetto e il lavoro è chiaro, **non farla tu**: delega il progetto interessato con
`facetoface_consult`, dicendogli cosa va cambiato e perché, e riferisci all'utente
l'esito. Vale anche quando sembra una cosa da due minuti, quando la cartella
dell'altro progetto è lì a portata di mano e quando quel progetto è un tuo antenato o
un tuo figlio: leggere per capire si può, toccare no. Se il lavoro tocca più
progetti, fai la parte di qui e delega il resto. Se la delega non riesce (l'altro
progetto non risponde), dillo e proponi una strada: non ripiegare modificandolo tu.

**Prima di chiudere: lo stato di git.** Quando il lavoro è finito e la
conversazione sta per chiudersi — l'utente saluta o dice una frase finale («grazie»,
«a domani», «chiudiamo qui», «per ora basta») — non congedarti senza aver guardato
il repository. Se questa cartella è un repo git, esegui `git status -sb` (mostra
anche i commit non pushati, `ahead N`) e riferisci **in breve** cosa resta aperto:
modifiche non committate, file nuovi non tracciati, commit non ancora pushati. Se è
tutto pulito e allineato, dillo in una riga. È un **promemoria per l'utente**, non
un permesso: non committare e non pushare di tua iniziativa — proponi e lascia
decidere, a meno che l'utente non te l'abbia già chiesto in questa conversazione.

## Comportamento
- Icona "VPN": verde = connesso, grigio = disconnesso
- Al clic: stato, server in uso, IP/luogo pubblici; azioni Connect/Disconnect/Refresh/Quit
- Notifiche desktop ai cambi di stato

## Stack e struttura
- Python (indicatore GNOME), icone SVG/PNG
- `cyberghost-indicator.py`, `icons/`, `install.sh`, `uninstall.sh`, `make-icons.py`

## Convenzioni
- Dipende dal comando `cyberghostvpn` installato nel sistema.

## Riferimenti
- Repo: https://github.com/andreagosto/cyberghost-status-indicator
