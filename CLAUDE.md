# CLAUDE.md — Benvenuti a Milano (Claude Impact Lab Milano, 3 ottobre 2026)

## Cosa stiamo costruendo

Siamo un team del Claude Impact Lab Milano, **Track 01 · Welcome journey for people arriving in Milan**.
La domanda del giorno: come può l'AI rendere più accessibili i servizi del Comune di Milano, per persone
con disabilità, anziani, chi non parla italiano, chi vede poco?

**Utente:** una persona appena arrivata a Milano che non parla bene l'italiano. Caso pilota inventato:
Ana, 24 anni, brasiliana, arrivata ieri con visto per studio per un master al Politecnico; scrive in
portoghese e ha difficoltà a leggere testi piccoli.
**Risultato:** in pochi minuti, nella sua lingua e anche a voce, ottiene il suo piano personale: quali
pratiche, in che ordine, entro quali date, in quale ufficio, con quali fonti ufficiali. Allo sportello
l'operatore apre lo stesso piano dal QR e Claude gli prepara risposte con le fonti.

## Non negoziabili (dalle regole del Lab)

- **Gira su Claude.** Claude fa il lavoro vero a runtime tramite l'API Anthropic: capisce la persona in
  qualsiasi lingua, sceglie il profilo, decide cosa chiedere, ragiona sulle regole del catalogo,
  costruisce il piano e risponde con le fonti. Test: spegni l'AI e non resta un piano, resta solo un
  catalogo statico.
- **Nessun dato personale.** Mai nomi, documenti, indirizzi, email reali. Casi inventati. Il percorso è
  identificato da un codice casuale. Le conversazioni non si salvano su disco.
- **Un umano decide.** Claude propone; il cittadino conferma il profilo prima del piano; l'operatore
  approva le risposte prima che arrivino al cittadino. Ogni affermazione su regole del Comune mostra
  la fonte.
- **Claude non inventa fatti.** Può usare solo procedure, scadenze, link e fonti presenti in
  `data/procedures.yaml` e nei dataset del Comune. Le date le calcola il codice, non il modello.
- **Chiavi API** solo in `.env` (in `.gitignore`). Mai nel repo.
- **Nessun lavoro precedente.** Il nucleo si costruisce oggi. Librerie e materiale di riferimento sì.
- **Time box:** consegna alle 16:00. Prima che funzioni, poi che sia bello.

## Stack

Python 3.12+ · Flask · una sola pagina HTML/CSS/JS senza framework (partendo da `docs/mockup.html`)
· `anthropic` SDK · `segno` per i QR in SVG · `PyYAML` · `python-dotenv`.
Windows, PowerShell. Avvio: `python app.py`, poi http://localhost:5000.

Modello a runtime: `claude-sonnet-5-5` (variabile `CLAUDE_MODEL`). Abbiamo crediti API limitati:
massimo 6 giri di tool per richiesta, `max_tokens` contenuti, niente chiamate in loop o all'avvio.

## Dati e fonti

- `data/procedures.yaml`: catalogo verificato oggi, con regole del nucleo, regole degli strumenti,
  punti in conflitto, e per ogni procedura scadenza, dipendenze, canale, istruzioni, link e fonti.
- Open data del Comune via API CKAN (vedi `_hub/DATA.md` e `_hub/starter/portal.py`):
  - `ds549-sedi-dei-servizi-anagrafici` (uffici anagrafe con coordinate);
  - `ds535_atm-fermate-linee-metropolitane` (fermate metro, per "abito vicino a…");
  - `ds94-infogeo-atenei-sedi-localizzazione` (sedi universitarie).
  Scaricati una volta e messi in cache in `data/cache/`, con copia di riserva nel repo.
- Pagine pubbliche: comune.milano.it, yesmilano.it, ANPR, Poste, Regione Lombardia, Agenzia delle
  Entrate (URL e data di consultazione già nel catalogo).

## Definizione di fatto

- La demo funziona dall'inizio alla fine sul caso di Ana (e sul secondo caso inventato in
  `docs/PERSONAS_E_STORIE.md`).
- Il README segue `_hub/templates/PROJECT_README.md`, compresa la sezione "Where Claude works".
- Esiste una registrazione dello schermo di due minuti.
