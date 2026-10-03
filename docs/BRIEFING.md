# Arrivare a Milano — Briefing di progetto

*Stato al 3 ottobre 2026 — versione integrata*

> Questa versione unisce due linee di lavoro: il sito Flask già sviluppato e la demo interattiva
> "Benvenuti a Milano", costruita in parallelo per il pitch. Le parti che arrivano dalla demo sono
> segnate con **(nuovo)**. La demo è consultabile qui:
> https://claude.ai/artifact/WbqHLNRHZWgyuKDJrDAF9p

## In una frase

Un sistema unico che aiuta chi arriva a Milano a capire **quali pratiche deve fare, in che ordine e
dove**, in base alla cittadinanza, al motivo dell'arrivo e a **chi si trasferisce con lui**. Ha due
facce collegate: un **portale per il cittadino** e una **console per gli operatori di sportello**.

## Il problema

Chi si trasferisce a Milano deve muoversi tra molti enti: consolato, Prefettura, Questura, Poste,
Comune, Agenzia delle Entrate, servizio sanitario. Le procedure cambiano molto in base alla
situazione, ad esempio tra un cittadino UE che viene a lavorare e uno studente extra UE. Le
informazioni sono sparse su siti diversi. I dati aperti del Comune descrivono la città, ma non
dicono a una persona *cosa deve fare*.

**(nuovo) Cosa è emerso dall'analisi dei portali del Comune:**

- **I dati sono ordinati e fruibili.** Il Portale del Dato è un catalogo di circa 2.600 dataset,
  in gran parte CSV e JSON, interrogabile via API CKAN e descritto secondo lo standard DCAT-AP_IT.
  MilanoStatistica vi è già confluita. Le chiavi per incrociare i dataset sono territoriali e
  temporali: municipio, NIL (quartiere), indirizzo, anno e mese. I Linked Open Data esistono, ma
  coprono poche decine di dataset.
- **Le procedure non sono dati.** Su comune.milano.it e YesMilano sono pagine web e PDF: non c'è
  un catalogo dei servizi interrogabile, ed entrambi i siti bloccano l'accesso automatico.
- **Le informazioni a volte si contraddicono.** Esempio concreto: per l'iscrizione sanitaria
  volontaria degli studenti extra UE una pagina universitaria indica ancora 149,77 €, mentre altre
  fonti riportano 700 € l'anno. È l'argomento più forte per il pitch.

## La soluzione

### Portale cittadino

1. **Capire chi sono**
   - **Chi si trasferisce (nuovo):** solo io, la mia famiglia, oppure più persone senza legami di
     famiglia (coinquilini). Per ogni persona si indicano legame, cittadinanza, motivo e se è
     minorenne. Non servono nomi: il sistema usa "Tu", "Persona 2" e così via.
   - **Profilo di ogni persona:** uno dei 14 profili, individuato in tre modi:
     - scelto da un elenco;
     - con 2–4 domande guidate (cittadinanza, durata, motivo);
     - con la **chat AI**. **(nuovo)** La persona si descrive liberamente nella propria lingua,
       scrivendo o dettando a voce. L'assistente riconosce composizione del nucleo, profili,
       data di arrivo e strumenti già posseduti, fa al massimo una domanda alla volta e non
       deduce mai la cittadinanza dal nome o dalla lingua.
   - **Data di arrivo (nuovo):** serve a trasformare le scadenze in date vere.
   - **Cosa ho già (nuovo, facoltativo):** email, numero di cellulare, SIM italiana, dispositivo
     con internet, SPID o CIE.

2. **Cosa devo fare**: un **piano personale**. Resta la divisione in fasi: *Prima di partire*,
   *Appena arrivato*, *Per stabilirti*, *Rinnovi e passi successivi*. **(nuovo)** Dentro le fasi
   i passi sono ordinati per scadenza e dipendenze: niente residenza prima del permesso, niente
   medico prima della residenza. Per ogni passo:
   - **(nuovo)** la scadenza calcolata, distinguendo scadenza di legge, data consigliata e data
     limite, e la priorità: urgente, importante o da pianificare;
   - **(nuovo)** per chi è il passo e, per le dichiarazioni di residenza, chi deve firmare;
   - **(nuovo)** il canale: online, online o di persona, solo di persona, nessuna azione da parte
     tua, oppure canale da verificare;
   - **(nuovo)** link distinti per tipo: servizio online, informazioni ufficiali, strumento. Ogni
     link porta i requisiti (per esempio "serve SPID o CIE") e l'indicazione "da confermare" se
     l'indirizzo non è verificato;
   - l'ente e dove presentarsi di persona;
   - le istruzioni numerate, i documenti e i costi;
   - le fonti e lo stato di verifica: fonte ufficiale, fonte secondaria, da verificare, fonti in
     conflitto;
   - **(nuovo)** un **QR del passo**, da mostrare allo sportello indicato, e la casella "Fatto".

3. **Domande sul piano (nuovo):** dopo la creazione del piano, la stessa chat risponde nella
   lingua della persona usando **solo** i contenuti del piano. Segnala quando un'informazione è da
   verificare e rimanda allo sportello quando la risposta non c'è.

### Console sportello (nuovo)

- L'operatore apre il percorso con il **codice del percorso** (esempio `MI-7K4Q`) oppure con il
  **QR di un passo** (esempio `MI-7K4Q-3`): la console si apre direttamente su quel passo.
- Vede composizione del nucleo, lingua del cittadino, data di arrivo, piano completo e passi
  segnati come fatti.
- Vede l'ultima domanda del cittadino nella lingua originale e, **solo se il cittadino l'ha
  consentito**, un riassunto in italiano della sua situazione, senza nomi né documenti.
- **Assistente AI dell'operatore:** interroga il catalogo e le procedure del Comune. Non decide al
  posto dell'operatore: mostra le fonti e, quando non concordano, mette in evidenza il conflitto.
- **Segnala al catalogo:** l'operatore segnala un'informazione superata. Il passo torna "da
  verificare" finché la redazione non lo conferma.

### Catalogo e redazione (nuovo)

Le segnalazioni degli operatori alimentano una coda di revisione dei contenuti. È la risposta
alla domanda aperta "chi aggiorna i contenuti": chi sta allo sportello si accorge per primo di
quello che cambia.

## Regole che il piano applica (nuovo)

Verificate durante la progettazione della demo. Tra parentesi la qualità della fonte.

**Residenza**
- Va dichiarata entro 20 giorni dal trasferimento. L'iscrizione avviene entro 2 giorni lavorativi
  e il Comune può verificare la dimora entro 45 giorni (fonti secondarie concordi).
- ANPR online vale solo per chi è già iscritto in un comune italiano o all'AIRE. Le persone
  straniere che arrivano dall'estero usano la procedura specifica del Comune di Milano (fonti
  ufficiali).
- **Famiglia anagrafica:** persone legate da matrimonio, unione civile, parentela, affinità,
  adozione, tutela o vincoli affettivi che vivono insieme. Fanno una sola dichiarazione; firmano
  tutti i maggiorenni e si includono i minori (DPR 223/1989 e prassi comunali).
- Se nello stesso nucleo ci sono provenienze diverse, per esempio un italiano da un altro comune e
  un familiare dall'estero, le dichiarazioni vanno separate per provenienza (prassi comunali).
- **Coinquilini senza legami:** formano nuclei anagrafici distinti allo stesso indirizzo, ognuno
  con la propria dichiarazione.
- Le dichiarazioni presentate da un tutore vanno fatte allo sportello.

**Permesso di soggiorno**
- Va chiesto entro 8 giorni lavorativi dall'ingresso, di norma con il kit postale (fonte ufficiale
  Poste).
- Per il lavoro dipendente viene prima il contratto di soggiorno allo Sportello Unico
  Immigrazione (fonti secondarie).
- I familiari di cittadini italiani o UE possono presentare la domanda in posta o in Questura
  (fonte ufficiale Poste).

**Codice fiscale**
- Di norma lo attribuisce lo Sportello Unico Immigrazione (lavoro dipendente) o la Questura, al
  rilascio del permesso.
- Altrimenti si chiede all'Agenzia delle Entrate con il modello AA4/8, in ufficio oppure via PEC.

**Sanità**
- La prima scelta del medico o del pediatra si fa di persona allo sportello Scelta e revoca
  dell'ASST. I cambi successivi si possono fare online dal Fascicolo Sanitario (fonte ufficiale
  Regione Lombardia).
- L'iscrizione volontaria degli studenti extra UE scade il 31 dicembre (fonte ufficiale Regione);
  l'importo è in conflitto tra le fonti.

**TARI**
- La dichiarazione di nuova occupazione va presentata entro 90 giorni.
- Si fa online con SPID o CIE, oppure inviando il modulo per email o raccomandata (fonte ufficiale
  Comune).
- Il cambio di residenza non la sostituisce.

**Strumenti abilitanti**
- Lo SPID accetta anche un numero di cellulare estero.
- Per una SIM italiana serve un documento d'identità e, di norma, il codice fiscale.
- Negli uffici postali si compra una SIM PosteMobile, attiva in poche ore.
- La carta d'identità elettronica si chiede al Comune dopo la residenza.
- Per lo SPID degli stranieri le fonti non concordano: alcune dicono che basta il permesso di
  soggiorno, un documento istituzionale dice che serve un documento italiano.

**Logica degli strumenti nel piano**
- Uno strumento compare solo se un passo successivo ne ha bisogno, con l'etichetta
  "necessario" o "consigliato".
- I suggerimenti sfruttano le visite già previste. Per esempio "già che sei in posta, compra la
  SIM", proposto solo a chi ha già il codice fiscale.

### Punti in conflitto o da verificare prima del lancio

| Punto | Stato |
|---|---|
| Importo dell'iscrizione sanitaria volontaria per studenti extra UE | Fonti in conflitto (700 € contro 149,77 €) |
| Chi effettua la verifica della dimora a Milano | Fonti in conflitto (messo comunale per YesMilano, Polizia locale per le guide di terzi) |
| SPID per cittadini stranieri con solo permesso di soggiorno | Fonti in conflitto |
| Indirizzo della pagina del Comune per la residenza di stranieri dall'estero | Link da confermare |
| Indirizzo pubblico della guida YesMilano per l'iscrizione sanitaria degli studenti | Link da confermare |
| Canale per l'iscrizione a scuola dei minori | Da verificare |
| TARI tra coinquilini: chi dichiara | Da verificare |

## Profili coperti

| Gruppo | Profili |
|---|---|
| Cittadini italiani | Trasferimento da altro Comune · Rientro dall'estero (AIRE) · Studente fuori sede |
| Cittadini UE, SEE e Svizzera | Soggiorno fino a 3 mesi · Lavoro oltre 3 mesi · Studio oltre 3 mesi · Soggiorno lungo con risorse proprie |
| Cittadini di altri Paesi | Visita breve (≤ 90 giorni) · Studio · Lavoro dipendente · Lavoro autonomo · Ricongiungimento familiare · Titolare di permesso di un altro Paese UE |
| Situazioni particolari | Familiari di cittadini italiani/UE, protezione internazionale e altri casi (solo rimandi agli enti) |

**(nuovo)** Il profilo si assegna **a ogni persona del nucleo**, non solo a chi compila. Il piano
unisce poi:
- i passi personali, come permesso, codice fiscale e sanità;
- i passi del nucleo, cioè la dichiarazione di residenza con chi la firma;
- i passi dell'abitazione, cioè la verifica della dimora e la TARI.

Per i minori si aggiungono pediatra e iscrizione a scuola.

## Stato dei lavori

| Area | Stato |
|---|---|
| Guida pubblica (profili, domande guidate, checklist, schede, uffici) | ✅ Funzionante e provata nel browser |
| Contenuti | ✅ 14 profili, 23 procedure, 9 enti, 7 domande guidate |
| Verifica dei contenuti | ⚠️ 14 procedure su 23 verificate sulle fonti ufficiali; 9 "da verificare" (segnalate nel sito) |
| Account con email + OTP | ✅ Funzionante in sviluppo (le email finiscono nel log del server) |
| Invio email reale | ⏳ Manca il server SMTP |
| Chat AI | ⏳ Codice pronto e testato con un client simulato; manca la chiave API Anthropic |
| Test automatici | ✅ 30 test superati |
| Pubblicazione online | ❌ Non ancora fatta |
| **(nuovo)** Demo interattiva per il pitch | ✅ Online: portale cittadino e console sportello collegati, piano con date e QR, nuclei, strumenti, chat AI multilingue con dettatura |
| **(nuovo)** Console sportello nel sito Flask | ❌ Da sviluppare |
| **(nuovo)** Piano con date, dipendenze e nuclei nel sito Flask | ❌ Da sviluppare |

## Fonti dei contenuti

Il punto di partenza è il documento di lavoro *Dashboard per chi arriva a Milano*, verificato
sulle fonti. Esito: dati corretti, un link non più valido e due precisazioni sul percorso del
lavoro non UE. I contenuti sono stati poi completati con pagine ufficiali di:

- Comune di Milano, ANPR (anagrafe nazionale) e Ministero dell'Interno;
- MAECI e portale *Il visto per l'Italia*;
- Polizia di Stato e Questura di Milano, Prefettura di Milano, Portale Immigrazione;
- Agenzia delle Entrate, Regione Lombardia, Ministero della Salute;
- Commissione europea, Your Europe, YesMilano Study & Work.
- **(nuovo)** Poste Italiane (permesso di soggiorno, PosteMobile, PosteID), ATS Milano (ricerca
  medico), Portale del Dato del Comune di Milano.

Ogni scheda mostra le sue fonti e la data di verifica. Le informazioni non ancora verificate
sono segnalate all'utente.

## Come è fatto

- **Tecnologia**: Python 3.13 e Flask, database SQLAlchemy (SQLite in sviluppo; PostgreSQL o
  SQL Server con una sola impostazione), HTML/CSS/JavaScript senza framework, adatto anche
  al telefono, con tema chiaro e scuro e stampa della checklist.
- **Contenuti separati dal codice**: profili, procedure, enti e domande stanno in 4 file YAML
  modificabili senza programmare. All'avvio il sito controlla che tutti i riferimenti siano
  coerenti.
- **Chat AI**: modello Claude Opus 5.5 tramite API Anthropic. Le istruzioni sono costruite
  automaticamente dall'elenco dei profili. Claude può solo scegliere uno dei profili esistenti,
  e lo fa tramite uno strumento con schema rigido. Le conversazioni non vengono salvate.
- **Email**: SMTP configurabile; testo + HTML; in sviluppo le email vengono scritte nel log.

### (nuovo) Campi da aggiungere al modello dei contenuti

Per far funzionare il piano della demo, ogni procedura nei YAML deve poter descrivere:

| Campo | A cosa serve |
|---|---|
| `canale` | online · misto · di persona · nessuna azione · da verificare |
| `link` | elenco tipizzato (servizio online, informazioni, strumento) con requisiti e stato verificato |
| `scadenza` | quantità, unità (giorni o giorni lavorativi), base (arrivo o passo precedente), natura (legale, consigliata, limite) |
| `priorita` | urgente · importante · da pianificare |
| `dipende_da` | passi che devono venire prima |
| `ambito` | persona · nucleo · abitazione |
| `firmatari` | per le dichiarazioni del nucleo: tutti i maggiorenni |
| `si_applica_a` | profili, minori, ruolo nel nucleo, provenienza (da altro comune o dall'estero) |
| `strumento` | per email, telefono, SIM, dispositivo, SPID e CIE: necessario o consigliato, e a quali passi serve |
| `suggerimenti` | consigli contestuali con condizione, per esempio "già che sei in posta" se manca la SIM e c'è il codice fiscale |

**Standard consigliato:** descrivere le procedure in modo compatibile con CPSV-AP_IT, il modello
nazionale per i servizi pubblici. Così il catalogo resta riusabile dal Comune.

### (nuovo) Dati aperti del Comune

- **Primo uso concreto:** le scuole e gli uffici vicino all'indirizzo del cittadino, collegati
  tramite il codice NIL del quartiere. Copre sia il passo "scuola" sia la "mappa degli uffici"
  già prevista.
- **Accesso:** API CKAN del Portale del Dato, con copia locale aggiornata periodicamente, così il
  sito non dipende dalla disponibilità del portale.
- **Altro dato utile:** il WiFi pubblico gratuito Open Wifi Milano, da suggerire a chi non ha un
  dispositivo connesso.

## Sicurezza e privacy

- Codici OTP:
  - non sono salvati in chiaro;
  - valgono 10 minuti, con al massimo 5 tentativi e un solo codice valido alla volta;
  - ci sono limiti di invio per email e per indirizzo IP.
- Il sito non rivela se un'email è registrata.
- Cookie di sessione protetti. Tutti i moduli hanno la protezione contro le richieste fatte da
  altri siti a nome dell'utente (CSRF).
- Dati conservati per utente, e solo questi: email, profilo, passi completati, note, registro
  delle email inviate.
- L'utente può **eliminare account e dati** in qualsiasi momento.
- Limiti di utilizzo sulla chat AI e sulle email di istruzioni, per evitare abusi e costi.
- **(nuovo) Uso anonimo come impostazione di base.**
  - Il percorso è identificato da un codice casuale e i QR contengono solo codice e numero del
    passo.
  - I componenti del nucleo non hanno nome.
  - L'account resta facoltativo.
- **(nuovo) Riassunto per lo sportello solo con consenso.** Il cittadino lo condivide spuntando
  una casella, e l'AI è istruita a non includervi nomi, numeri di documento, indirizzi, recapiti
  o informazioni sulla salute.
- **(nuovo) Operatori autenticati e tracciati.** Gli accessi alla console vanno registrati e i
  percorsi aperti dagli operatori devono scadere.

## Cosa serve per andare online

1. **Server SMTP** su un dominio di proprietà, ad esempio un account SMTP del dominio,
   Brevo, Mailjet o Amazon SES, per inviare codici e istruzioni.
2. **Chiave API Anthropic** per attivare la chat. Il sito funziona anche senza.
3. **`SECRET_KEY`** casuale nel file `.env`.
4. **Hosting** con HTTPS, un server di produzione (es. Waitress o Gunicorn) e un database
   adatto, se il traffico lo richiede.
5. **Revisione dei contenuti** "da verificare" prima della pubblicazione, compresi i punti in
   conflitto elencati sopra.

## Prossimi passi proposti

1. **(nuovo)** Estendere il modello dei contenuti con i campi del piano e calcolare scadenze,
   dipendenze e priorità a partire dalla data di arrivo.
2. **(nuovo)** Gestire il nucleo: singolo, famiglia, coinquilini, con passi personali, del nucleo
   e dell'abitazione.
3. **(nuovo)** Console sportello: accesso operatori, apertura da codice o QR, assistente AI
   dell'operatore, segnalazioni al catalogo.
4. **(nuovo)** Strumenti abilitanti con i suggerimenti contestuali.
5. Spostare le istruzioni della chat in un file `.md` modificabile e aggiungere a ogni profilo
   i criteri di scelta. **(nuovo)** Estendere la chat al riconoscimento del nucleo e degli
   strumenti, e alle domande sul piano.
6. Provare la chat con conversazioni di esempio appena c'è la chiave API.
7. Completare la verifica delle 9 procedure aperte e dei punti in conflitto, e inserire gli
   indirizzi ufficiali degli uffici.
8. Versione in inglese e, in seguito, in altre lingue. **(nuovo)** La chat già risponde nella
   lingua della persona; il piano va tradotto.
9. Promemoria email automatici sulle scadenze, compresi i rinnovi: permesso, iscrizione sanitaria
   al 31 dicembre, rinnovo della dichiarazione di dimora abituale per i cittadini extra UE.
10. Mappa degli uffici e delle scuole con i dati aperti del Comune.
11. Percorsi dedicati per familiari di cittadini UE/italiani e per la protezione internazionale.
12. **(nuovo)** Prova sul campo con 5–10 persone appena arrivate, per esempio tramite lo sportello
    studenti di YesMilano o un'associazione del territorio.

## Decisioni già prese (nuovo)

- Il progetto parte come iniziativa **esterna e indipendente**, non commissionata dal Comune.
- Il pitch è rivolto al **Comune (assessorato competente) e a YesMilano**.
- Primo evento di vita: **arrivo e residenza**.
- Canale iniziale: **solo web**. Totem o postazioni assistite allo sportello vengono dopo.
- Lingue della demo: **italiano e inglese**.
- Prima demo come **mockup cliccabile per il pitch**, da cui partire per l'applicativo.

## Decisioni ancora aperte

- Fornitore SMTP e dominio di invio.
- Hosting e database di produzione.
- Lingue da supportare al lancio.
- Chi cura e aggiorna i contenuti, e con quale frequenza di verifica.
- Eventuale informativa privacy formale (GDPR) e titolare del trattamento.
- **(nuovo)** Come autenticare gli operatori di sportello finché il progetto non è adottato dal
  Comune: account dimostrativi oppure accesso per enti partner.
- **(nuovo)** Se il calcolo delle scadenze debba tenere conto delle festività.
