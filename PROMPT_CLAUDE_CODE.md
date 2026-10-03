# Prompt per Claude Code

Incolla tutto il blocco qui sotto in Claude Code, aperto nella cartella `C:\Dev\CLAUDE_IMPACT_LAB`.

---

```
Siamo al Claude Impact Lab Milano, oggi 3 ottobre 2026, Track 01 (Welcome journey).
Consegna alle 16:00: ogni scelta deve servire a una demo funzionante entro le 15:15.

LEGGI PRIMA, in quest'ordine, e non scrivere codice finché non hai finito:
1. CLAUDE.md (regole non negoziabili, utente, stack)
2. docs/PERSONAS_E_STORIE.md (le user stories da soddisfare)
3. data/procedures.yaml (il catalogo: è la sola fonte di fatti sulle procedure)
4. docs/mockup.html (il mockup già validato: è il riferimento per aspetto e flussi)
5. _hub/CHALLENGE.md, _hub/RULES.md, _hub/DATA.md, _hub/starter/runs_on_claude.py,
   _hub/starter/portal.py, _hub/templates/PROJECT_README.md
6. docs/BRIEFING.md solo per contesto: è più grande di quello che costruiamo oggi.
Se _hub/ non esiste, clonalo: git clone https://github.com/Claude-Milano/impact-lab-oct-2026 _hub

Se nella cartella trovi già un'applicazione (per esempio un'app Flask di un collega), NON usarla come
base senza chiedermelo: per la regola 2 il nucleo deve essere costruito oggi. Costruisci nel tuo
codice nuovo.

Poi dimmi in 10 righe il piano, aspetta il mio ok e procedi per traguardi. A ogni traguardo:
fai un commit, dimmi come provarlo in PowerShell, e passa al successivo.

COSA COSTRUIRE

Un'app Flask (app.py) con una sola pagina web (templates/index.html + static/), che riusa la
grafica e i flussi di docs/mockup.html. Nel mockup le chiamate AI passano da window.claude: vanno
sostituite con chiamate fetch al backend, che usa l'API Anthropic. Il resto del mockup (profili a
pulsanti, piano, QR, console sportello) va semplificato secondo le priorità sotto.

Claude lavora a runtime come agente con tool use (schema di _hub/starter/runs_on_claude.py):
system prompt in prompts/agent_citizen.md e prompts/agent_counter.md, caricati dal codice.

Tool dell'agente cittadino (in tools.py, tutti deterministici, senza dati personali):
- get_catalog(profile_ids) → procedure applicabili da data/procedures.yaml, con regole del nucleo,
  regole degli strumenti e punti in conflitto.
- compute_deadline(arrival_date, procedure_id) → data calcolata dal codice (giorni o giorni
  lavorativi, base data di arrivo o dichiarazione di residenza). Il modello non calcola date.
- find_offices(near) → uffici anagrafe più vicini da ds549-sedi-dei-servizi-anagrafici. "near" può
  essere una fermata metro (ds535_atm-fermate-linee-metropolitane), una sede universitaria
  (ds94-infogeo-atenei-sedi-localizzazione) o coordinate. Distanza in linea d'aria.
- propose_profile(...) → strumento con schema rigido: tipo di nucleo (single|family|group),
  persone (relazione, minorenne, cittadinanza ita|ue|extra, motivo work|study|family|other),
  data di arrivo, lingua, strumenti posseduti (email, telefono, SIM italiana, dispositivo,
  SPID/CIE), domanda di chiarimento se manca qualcosa. Il server restituisce una scheda che il
  cittadino deve CONFERMARE prima del piano.
- submit_plan(steps) → schema rigido: per ogni passo procedure_id del catalogo, per chi è,
  testo delle istruzioni nella lingua dell'utente, ufficio suggerito. Il server rifiuta id
  inesistenti e rimanda l'errore a Claude perché corregga, controlla l'ordine rispetto a
  dipende_da, aggiunge LUI date, link e fonti presi dal catalogo (Claude non può inventare URL).

Regole per il system prompt del cittadino:
- risponde nella lingua in cui scrive la persona, con frasi semplici;
- non deduce mai la cittadinanza da nome o lingua; fa al massimo una domanda alla volta;
- usa i tool prima di affermare fatti; dice quando una fonte è secondaria o in conflitto;
- non chiede e non conserva dati personali (nomi, documenti, indirizzi esatti, email);
- applica le regole del nucleo e degli strumenti del catalogo.

Endpoint minimi:
- POST /api/chat {session_id, message} → risposta dell'agente e, se c'è, la scheda profilo.
- POST /api/confirm {session_id} → l'agente costruisce il piano; risposta JSON con codice percorso
  casuale (es. MI-7K4Q), passi ordinati, date, stato di verifica, fonti, ufficio vicino.
- GET /api/plan/<code> e GET /api/plan/<code>.ics (scadenze nel calendario: è la parte
  "proattiva" senza dati personali).
- GET /qr/<code>/<n>.svg → QR del passo con segno.
- POST /api/counter/ask {code, question} → agente sportello: bozza di risposta con fonti dal
  catalogo, conflitti in evidenza; l'operatore la approva o la corregge nella pagina.
Stato solo in memoria (dict con scadenza), niente database, niente salvataggio delle chat.

PRIORITÀ E TRAGUARDI

T1 (entro 30 min): app che parte, catalogo caricato e validato all'avvio, dataset ds549/ds535/ds94
   scaricati in data/cache/ con fallback offline, tool funzionanti e testati con pytest.
T2 (entro 60 min): chat → scheda profilo da confermare → piano con date, fonti, stati, ufficio più
   vicino e QR, sul caso di Ana in portoghese. Questo è il cuore: se il tempo stringe, si taglia
   tutto il resto, non questo.
T3 (entro 80 min): accessibilità: dettatura vocale (Web Speech API, con messaggio se non
   disponibile), pulsante "Ascolta" che legge risposta e piano (speechSynthesis), testo grande,
   contrasto alto, navigazione da tastiera. Esportazione .ics.
T4 (entro 100 min): vista sportello: apre il piano dal codice o dal QR, bozza di risposta di
   Claude con fonti, pulsante "Approva".
T5 (solo se avanza tempo): famiglia e coinquilini (caso Vikram), strumenti abilitanti nel piano.

CONSEGNA (da fare comunque, alle 15:15 al più tardi)
- README.md dal template del Lab, partendo dalla bozza già presente in README.md. Aggiorna la
  sezione "Where Claude works" con i dettagli reali: modello, file dei prompt, tool, cosa decide
  Claude, cosa conferma l'umano, cosa succede se sbaglia.
- Tabella "City data and sources" con gli slug dei dataset e le pagine usate, con data.
- requirements.txt, .env.example, istruzioni di avvio per Windows PowerShell.
- Controlla che non ci siano chiavi API o dati personali nel repo.

STILE DI LAVORO
- Codice semplice e leggibile, niente architetture superflue.
- Ogni chiamata a Claude: max 6 giri di tool, max_tokens contenuti, gestione degli errori con un
  messaggio chiaro nella pagina.
- Se un dataset ha colonne diverse da quelle che ti aspetti, ispezionalo con portal.py e adattati.
- Se una scelta non è coperta da queste istruzioni, scegli la più semplice e dimmelo in una riga.
```
