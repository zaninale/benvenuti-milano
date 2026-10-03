/* Benvenuti a Milano: una sola pagina. Ogni chiamata AI passa dal backend Flask, che usa Claude. */
(function () {
"use strict";

var TX = {
 it: {
  demo: "Demo: passa da una parte all'altra del servizio", tabCit: "Cittadino",
  brand: "Benvenuti a Milano", tag: "Prototipo non ufficiale", langLabel: "Lingua", big: "A+", contrast: "Contrasto",
  h1: "Arrivi a Milano? Ecco cosa fare, in che ordine e dove.",
  lead: "Raccontaci di te nella tua lingua, scrivendo o a voce: Claude ti prepara il piano con date, uffici e fonti ufficiali del Comune.",
  aiTitle: "Raccontaci di te",
  aiHint: "Scrivi o detta nella tua lingua chi si trasferisce, perché sei a Milano, quando sei arrivato e vicino a quale fermata della metro abiti. Non servono nomi né documenti.",
  aiLabel: "Il tuo messaggio, in qualsiasi lingua",
  ph: "Per esempio: sono brasiliana, sono arrivata ieri per un master al Politecnico, abito vicino alla fermata Piola.",
  ph2: "Fai una domanda sul tuo piano, in qualsiasi lingua",
  send: "Invia", mic: "Detta", micStop: "Ferma", micLang: "Lingua della dettatura", listen: "Ascolta", stop: "Ferma",
  thinking: "Claude sta leggendo il tuo messaggio…",
  building: "Claude sta costruendo il tuo piano dal catalogo del Comune: ci vuole circa mezzo minuto…",
  empty: "Scrivi o detta qualcosa prima di inviare.", netErr: "Il server non risponde. Controlla che l'app sia avviata e riprova.",
  noMic: "La dettatura non è disponibile in questo browser: prova con Chrome o Edge, oppure usa il microfono della tastiera.",
  micDenied: "Il microfono non è accessibile: controlla i permessi del browser.", listening: "Ti ascolto… premi Ferma quando hai finito.",
  noTts: "La lettura ad alta voce non è disponibile in questo browser.",
  cardTitle: "Ecco cosa ho capito: è giusto?", confirm: "Confermo, crea il mio piano", confirmed: "Confermata",
  missing: "Manca ancora: ", cardHint: "Se qualcosa non va, scrivilo nel messaggio qui sotto.",
  who: {single: "Solo io", family: "La mia famiglia", group: "Più persone, senza legami di famiglia"},
  rel: {self: "Tu", partner: "Coniuge o partner", child: "Figlio o figlia", relative: "Altro familiare", mate: "Coinquilino"},
  cit: {ita: "Cittadinanza italiana", ue: "Cittadinanza UE", extra: "Cittadinanza extra-UE"},
  mot: {work: "per lavoro", study: "per studio", family: "per famiglia", other: "altro motivo"},
  minor: "minorenne", person: "Persona ", arrival: "Arrivo", near: "Vicino a", lang: "Lingua",
  has: "Hai già", hasNot: "Non hai ancora",
  tools: {email: "email", telefono: "numero di cellulare", sim_italiana: "SIM italiana", dispositivo: "smartphone o computer", spid_cie: "SPID o CIE"},
  planTitle: "Il tuo piano", legend: "Affidabilità:",
  st: {fonte_ufficiale: "Fonte ufficiale", fonte_secondaria: "Fonte secondaria", da_verificare: "Da verificare", fonti_in_conflitto: "Fonti in conflitto"},
  pri: {urgente: "Urgente", importante: "Importante", da_pianificare: "Da pianificare"},
  nat: {scadenza_di_legge: "scadenza di legge", data_consigliata: "data consigliata", data_limite: "possibile fino a"},
  mode: {online: "Puoi farlo online", online_o_di_persona: "Online o di persona", di_persona: "Solo di persona", nessuna_azione: "Nessuna azione da parte tua", da_solo: "Lo fai da solo", da_verificare: "Canale da verificare"},
  lk: {servizio_online: "Servizio online", informazioni: "Informazioni ufficiali", strumento: "Strumento"},
  ftipo: {ufficiale: "fonte ufficiale", istituzionale: "fonte istituzionale", secondaria: "fonte secondaria", link_da_confermare: "link da confermare"},
  need: {necessario: "Strumento necessario", consigliato: "Strumento consigliato"},
  unconf: "Link da confermare", after: "Dopo il passo ", asap: "Appena possibile", done: "Fatto", showAt: "Mostra a: ",
  officeHere: "Ufficio consigliato: ", sources: "Fonti", checked: "consultata il ", forWho: "Per: ", signers: "Firmano: ",
  codeTitle: "Il tuo codice", codeLabel: "Codice del percorso", codeNote: "Valido 7 giorni. Non contiene dati personali.",
  codeHint: "Ogni passo ha il suo QR: mostralo allo sportello indicato. Il codice apre tutto il percorso.",
  listenPlan: "Ascolta il piano", ics: "Aggiungi al calendario", pdf: "Scarica PDF", mail: "Invia per email",
  mailSubject: "Il mio piano Benvenuti a Milano", mailBody: "Ecco il mio piano per le pratiche a Milano.",
  mailAttach: "Allega il PDF appena scaricato.",
  officeTitle: "Anagrafe più vicina", km: "km in linea d'aria da ", officeSrc: "Open data del Comune di Milano: ",
  answersTitle: "Risposte dallo sportello", approved: "Approvata dall'operatore il ",
  conflictTitle: "Dove le fonti non concordano", conflictHint: "Su questi punti fatti confermare l'informazione allo sportello.",
  foot: "Demo indipendente, non realizzata dal Comune di Milano. Le informazioni vanno sempre confermate sulle fonti ufficiali indicate.",
  step: "Passo ",
  entryChat: "Scrivi o detta", entryForm: "Compila le schede", formTitle: "Compila le schede",
  formHint: "Rispondi alle domande: Claude prepara il piano dopo che hai confermato la scheda. Non servono nomi né documenti.",
  formBtn: "Prepara la scheda", formMsg: "Ecco la tua scheda: controllala e conferma.",
  citS: {ita: "Italiana", ue: "Paese UE", extra: "Paese extra-UE"}, motS: {work: "Lavoro", study: "Studio", family: "Famiglia", other: "Altro"},
  relL: "Legame", citL: "Cittadinanza", motL: "Motivo", minorL: "Minorenne", sitL: "La tua situazione", choose: "Scegli…",
  addP: "Aggiungi persona", remove: "Rimuovi", arrL: "Data di arrivo a Milano", notYet: "Non sono ancora arrivato",
  nearL: "Fermata della metro o università vicina", nearPh: "Es. Piola o Politecnico", langPlan: "Lingua del piano",
  toolsL: "Cosa hai già", docsL: "Quali documenti hai già", notArrived: "Non ancora arrivato",
  docsHas: "Documenti che hai", docsMissing: "Documenti che non hai ancora", missingDoc: "Ti manca: ",
  working: "Claude sta lavorando", usually: "Di solito ci vogliono 20-30 secondi.", seconds: " secondi", busyBtn: "Sto pensando…",
  phases: {start: "Leggo la tua richiesta", get_catalog: "Leggo le regole del Comune", compute_deadline: "Calcolo le scadenze",
           find_offices: "Cerco l'ufficio anagrafe più vicino", propose_profile: "Preparo la tua scheda",
           submit_plan: "Controllo e preparo il piano", draft_answer: "Preparo la bozza con le fonti"}
 },
 en: {
  demo: "Demo: switch between the two sides of the service", tabCit: "Citizen",
  brand: "Welcome to Milan", tag: "Unofficial prototype", langLabel: "Language", big: "A+", contrast: "Contrast",
  h1: "Moving to Milan? Here's what to do, in what order and where.",
  lead: "Tell us about yourself in your own language, by text or voice: Claude builds your plan with dates, offices and the City's official sources.",
  aiTitle: "Tell us about yourself",
  aiHint: "Write or dictate in your language who is moving, why you are in Milan, when you arrived and which metro stop you live near. No names or documents needed.",
  aiLabel: "Your message, in any language",
  ph: "For example: I'm from Brazil, I arrived yesterday for a master's at the Politecnico, I live near Piola metro stop.",
  ph2: "Ask a question about your plan, in any language",
  send: "Send", mic: "Dictate", micStop: "Stop", micLang: "Dictation language", listen: "Listen", stop: "Stop",
  thinking: "Claude is reading your message…",
  building: "Claude is building your plan from the City's catalogue: it takes about half a minute…",
  empty: "Write or dictate something before sending.", netErr: "The server isn't answering. Check the app is running and try again.",
  noMic: "Dictation isn't available in this browser: try Chrome or Edge, or use your keyboard's microphone.",
  micDenied: "The microphone can't be reached: check the browser permissions.", listening: "Listening… press Stop when you're done.",
  noTts: "Reading aloud isn't available in this browser.",
  cardTitle: "Here's what I understood: is it right?", confirm: "Confirm and build my plan", confirmed: "Confirmed",
  missing: "Still missing: ", cardHint: "If something is wrong, write it in the message below.",
  who: {single: "Just me", family: "My family", group: "Several people, not family"},
  rel: {self: "You", partner: "Spouse or partner", child: "Son or daughter", relative: "Other relative", mate: "Housemate"},
  cit: {ita: "Italian citizen", ue: "EU citizen", extra: "Non-EU citizen"},
  mot: {work: "for work", study: "for study", family: "for family", other: "other reason"},
  minor: "under 18", person: "Person ", arrival: "Arrival", near: "Near", lang: "Language",
  has: "You have", hasNot: "You don't have yet",
  tools: {email: "email", telefono: "mobile number", sim_italiana: "Italian SIM", dispositivo: "smartphone or computer", spid_cie: "SPID or CIE"},
  planTitle: "Your plan", legend: "Reliability:",
  st: {fonte_ufficiale: "Official source", fonte_secondaria: "Secondary source", da_verificare: "To be verified", fonti_in_conflitto: "Conflicting sources"},
  pri: {urgente: "Urgent", importante: "Important", da_pianificare: "Plan ahead"},
  nat: {scadenza_di_legge: "legal deadline", data_consigliata: "recommended date", data_limite: "possible until"},
  mode: {online: "You can do it online", online_o_di_persona: "Online or in person", di_persona: "In person only", nessuna_azione: "Nothing for you to do", da_solo: "On your own", da_verificare: "Channel to be verified"},
  lk: {servizio_online: "Online service", informazioni: "Official information", strumento: "Tool"},
  ftipo: {ufficiale: "official source", istituzionale: "institutional source", secondaria: "secondary source", link_da_confermare: "link to be confirmed"},
  need: {necessario: "Required tool", consigliato: "Recommended tool"},
  unconf: "Link to be confirmed", after: "After step ", asap: "As soon as possible", done: "Done", showAt: "Show at: ",
  officeHere: "Suggested office: ", sources: "Sources", checked: "checked on ", forWho: "For: ", signers: "Signed by: ",
  codeTitle: "Your code", codeLabel: "Journey code", codeNote: "Valid for 7 days. It holds no personal data.",
  codeHint: "Each step has its own QR: show it at the desk listed. The code opens your whole journey.",
  listenPlan: "Listen to the plan", ics: "Add to calendar", pdf: "Download PDF", mail: "Send by email",
  mailSubject: "My Welcome to Milan plan", mailBody: "Here is my plan for the procedures in Milan.",
  mailAttach: "Attach the PDF you just downloaded.",
  officeTitle: "Nearest registry office", km: "km as the crow flies from ", officeSrc: "City of Milan open data: ",
  answersTitle: "Answers from the desk", approved: "Approved by the officer on ",
  conflictTitle: "Where sources disagree", conflictHint: "Have these points confirmed at the desk.",
  foot: "Independent demo, not made by the City of Milan. Always confirm information on the official sources listed.",
  step: "Step ",
  entryChat: "Write or dictate", entryForm: "Fill in the forms", formTitle: "Fill in the forms",
  formHint: "Answer the questions: Claude builds the plan after you confirm the card. No names or documents needed.",
  formBtn: "Prepare the card", formMsg: "Here is your card: check it and confirm.",
  citS: {ita: "Italian", ue: "EU country", extra: "Non-EU country"}, motS: {work: "Work", study: "Study", family: "Family", other: "Other"},
  relL: "Relationship", citL: "Citizenship", motL: "Reason", minorL: "Under 18", sitL: "Your situation", choose: "Choose…",
  addP: "Add person", remove: "Remove", arrL: "Arrival date in Milan", notYet: "I haven't arrived yet",
  nearL: "Nearby metro stop or university", nearPh: "E.g. Piola or Politecnico", langPlan: "Plan language",
  toolsL: "What you already have", docsL: "Which documents you already have", notArrived: "Not arrived yet",
  docsHas: "Documents you have", docsMissing: "Documents you don't have yet", missingDoc: "You still need: ",
  working: "Claude is working", usually: "It usually takes 20-30 seconds.", seconds: " seconds", busyBtn: "Thinking…",
  phases: {start: "Reading your request", get_catalog: "Reading the City's rules", compute_deadline: "Working out the deadlines",
           find_offices: "Finding the nearest registry office", propose_profile: "Preparing your card",
           submit_plan: "Checking and preparing the plan", draft_answer: "Drafting the answer with sources"}
 }
};

var S = {lang: (navigator.language || "it").slice(0, 2) === "it" ? "it" : "en", langTouched: false, sid: null,
         thread: [], busy: false, plan: null, done: {}, op: null, opStep: null, draft: null, speaking: false};

function $(id) { return document.getElementById(id); }
function t(k) { return TX[S.lang][k]; }
function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function fmtDate(iso, lang) {
  if (!iso) return "";
  var p = iso.split("-"), d = new Date(+p[0], +p[1] - 1, +p[2]);
  try { return d.toLocaleDateString(lang || S.lang, {weekday: "short", day: "numeric", month: "long", year: "numeric"}); } catch (e) { return iso; }
}
function langName(tag) {
  try { return new Intl.DisplayNames([S.lang], {type: "language"}).of(tag); } catch (e) { return tag; }
}
function plain(s) { return String(s || "").replace(/\*\*|__/g, "").replace(/^#+\s*/gm, ""); }
function status(id, txt, isErr) { var el = $(id); el.textContent = txt || ""; el.style.color = isErr ? "var(--x-c)" : ""; }

async function api(url, body) {
  try {
    var r = await fetch(url, body ? {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)} : {});
    var data = {};
    try { data = await r.json(); } catch (e) { /* risposta non JSON */ }
    if (!r.ok && !data.error) data.error = t("netErr");
    return data;
  } catch (e) { return {error: t("netErr")}; }
}

/* ---------------------------------------------------------------- testi e lingua */

function renderStatic() {
  document.documentElement.lang = S.lang;
  document.querySelectorAll("#view-cit [data-t], .switch [data-t]").forEach(function (el) { el.textContent = t(el.getAttribute("data-t")); });
  document.querySelectorAll(".lbtn[data-lang]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-lang") === S.lang)); });
  $("msg").placeholder = S.plan ? t("ph2") : t("ph");
  micUI();
  renderThread();
  if (S.entry === "form") renderForm();
  if (S.plan) renderPlan();
}

/* ---------------------------------------------------------------- conversazione */

function push(m) { S.thread.push(m); renderThread(); }

function cardHTML(c, i, used) {
  var L = S.lang, T = TX[L], rows = [];
  rows.push("<b>" + esc(T.who[c.nucleo] || c.nucleo) + "</b>");
  var list = c.persone.map(function (p, k) {
    var who = p.relazione === "self" ? T.rel.self : T.person + (k + 1) + " (" + (T.rel[p.relazione] || p.relazione) + ")";
    var bits = [p.cittadinanza ? T.cit[p.cittadinanza] : "?"];
    if (p.profilo_nome) bits.unshift(p.profilo_nome);
    if (p.cittadinanza === "extra" && !p.minorenne && p.motivo) bits.push(T.mot[p.motivo]);
    if (p.minorenne) bits.push(T.minor);
    return "<li>" + esc(who) + ": " + esc(bits.join(", ")) + "</li>";
  }).join("");
  rows.push('<ul class="mlist">' + list + "</ul>");
  if (c.data_arrivo) rows.push("<span>" + T.arrival + ": <b>" + esc(fmtDate(c.data_arrivo)) + "</b></span>");
  else if (c.gia_arrivato === false) rows.push("<span>" + T.arrival + ": <b>" + T.notArrived + "</b></span>");
  if (c.vicino_a) rows.push("<span>" + T.near + ": <b>" + esc(c.vicino_a) + "</b></span>");
  if (c.lingua) rows.push("<span>" + T.lang + ": <b>" + esc(langName(c.lingua)) + "</b></span>");
  var st = c.strumenti || {}, yes = [], no = [];
  Object.keys(T.tools).forEach(function (k) { if (st[k] === true) yes.push(T.tools[k]); if (st[k] === false) no.push(T.tools[k]); });
  if (yes.length) rows.push("<span>" + T.has + ": " + esc(yes.join(", ")) + "</span>");
  if (no.length) rows.push("<span>" + T.hasNot + ": " + esc(no.join(", ")) + "</span>");
  var dn = function (id) { var d = (S.opz && S.opz.documenti || []).filter(function (x) { return x.id === id; })[0]; return d ? (S.lang === "en" ? d.name_en : d.nome) : id; };
  var docs = c.documenti || {}, dy = [], dno = [];
  Object.keys(docs).forEach(function (k) { if (docs[k] === true) dy.push(dn(k)); if (docs[k] === false) dno.push(dn(k)); });
  if (dy.length) rows.push("<span>" + T.docsHas + ": " + esc(dy.join(", ")) + "</span>");
  if (dno.length) rows.push("<span>" + T.docsMissing + ": " + esc(dno.join(", ")) + "</span>");
  if (c.mancano && c.mancano.length) rows.push('<span class="unc">' + T.missing + esc(c.mancano.join(", ")) + "</span>");
  var action = "";
  if (c.completa) action = used ? '<span class="pill p-o" style="align-self:flex-start">' + T.confirmed + "</span>"
                                : '<button class="btn" data-confirm="' + i + '">' + T.confirm + "</button><small>" + T.cardHint + "</small>";
  return '<div class="pcard"><small>' + T.cardTitle + "</small>" + rows.join("") + action + "</div>";
}

function renderThread() {
  $("thread").innerHTML = S.thread.map(function (m, i) {
    if (m.k === "me") return '<div class="q-me" dir="auto">' + esc(m.text) + "</div>";
    if (m.k === "bot") return '<div class="q-bot" dir="auto"><span class="bot-txt">' + esc(plain(m.text)) + "</span></div>";
    if (m.k === "card") return cardHTML(m.card, i, m.used);
    if (m.k === "err") return '<p class="err">' + esc(m.text) + "</p>";
    return "";
  }).join("");
  $("thread").hidden = !S.thread.length;
  $("listenBtn").hidden = !S.thread.some(function (m) { return m.k === "bot"; });
}

function setBusy(on, msg) {
  S.busy = on;
  $("sendBtn").disabled = on;
  $("sendBtn").textContent = on ? t("busyBtn") : t("send");
  if (S.stopWork) { S.stopWork(); S.stopWork = null; }
  if (on && S.sid) S.stopWork = startWork("work", S.sid);
  document.querySelectorAll("[data-confirm]").forEach(function (b) { b.disabled = on; });
  status("status", on ? msg : "");
}

function handle(d) {
  if (d.session_id) S.sid = d.session_id;
  if (d.reply) push({k: "bot", text: d.reply});
  if (d.card) {
    push({k: "card", card: d.card});
    if (!S.langTouched && d.card.lingua && d.card.lingua.slice(0, 2) !== "it" && S.lang !== "en") { S.lang = "en"; renderStatic(); }
    var opt = Array.prototype.find.call($("micLang").options, function (o) { return o.value.slice(0, 2) === d.card.lingua.slice(0, 2); });
    if (opt) $("micLang").value = opt.value;
  }
  if (d.plan) { S.plan = d.plan; S.done = {}; renderPlan(); $("planCols").hidden = false; $("msg").placeholder = t("ph2");
                setTimeout(function () { $("planPanel").scrollIntoView({behavior: "smooth", block: "start"}); }, 150); }
  if (d.error) status("status", d.error, true);
}

async function send() {
  var txt = $("msg").value.trim();
  if (!txt) { status("status", t("empty"), true); $("msg").focus(); return; }
  if (S.busy) return;
  stopMic();
  push({k: "me", text: txt});
  $("msg").value = "";
  await ensureSession();
  setBusy(true, t("thinking"));
  var d = await api("/api/chat", {session_id: S.sid, message: txt});
  setBusy(false);
  handle(d);
}

async function confirmCard(i) {
  var m = S.thread[i];
  if (!m || m.used || S.busy) return;
  m.used = true;
  renderThread();
  setBusy(true, t("building"));
  var d = await api("/api/confirm", {session_id: S.sid});
  setBusy(false);
  if (d.error && !d.plan) { m.used = false; renderThread(); }
  handle(d);
}

/* ---------------------------------------------------------------- piano */

var ENTE = function (e) { return e.indexOf("Comune") === 0 ? "e-m" : e.indexOf("Sanit") === 0 ? "e-h" : e.indexOf("Strumento") === 0 ? "e-t" : "e-s"; };
var ST_CLS = {fonte_ufficiale: "p-o", fonte_secondaria: "p-s", da_verificare: "p-v", fonti_in_conflitto: "p-x"};
var PRI_CLS = {urgente: "pri-1", importante: "pri-2", da_pianificare: "pri-3"};
var MODE_CLS = {online: "mode-online", online_o_di_persona: "mode-mixed", di_persona: "mode-person", nessuna_azione: "mode-none", da_solo: "mode-self", da_verificare: "mode-none"};
var CAL = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="vertical-align:-2px;margin-right:6px"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path></svg>';

function dueHTML(s, plan, T, lang) {
  var sc = s.scadenza || {};
  if (sc.data) return '<span class="due">' + CAL + esc(fmtDate(sc.data, lang)) + ' <span class="after">· ' + esc(T.nat[sc.natura] || "") + "</span></span>";
  if (sc.regola) return '<span class="after">' + CAL + esc(sc.regola) + "</span>";
  if (s.dopo && s.dopo.length) return '<span class="after">' + T.after + Math.max.apply(null, s.dopo) + "</span>";
  return '<span class="after">' + T.asap + "</span>";
}

function stepHTML(s, plan, opts) {
  var T = TX[opts.lang], code = s.codice_passo, many = plan.scheda.persone.length > 1;
  var badges = (s.strumento ? '<span class="pill tool-' + (s.strumento === "necessario" ? "req" : "opt") + '">' + T.need[s.strumento] + "</span>" : "")
    + '<span class="pill ' + PRI_CLS[s.priorita] + '">' + T.pri[s.priorita] + "</span>"
    + '<span class="pill ' + ENTE(s.ente) + '">' + esc(s.ufficio) + "</span>"
    + '<span class="pill ' + ST_CLS[s.stato_verifica] + '">' + T.st[s.stato_verifica] + "</span>";
  var label = function (n) { return n === 1 ? T.rel.self : T.person + n; };
  var who = many ? '<span class="wholine">' + T.forWho + s.per_chi.map(label).join(", ") + "</span>" : "";
  var firmano = s.per_chi.filter(function (n) { return !plan.scheda.persone[n - 1].minorenne; });
  if (many && s.firmatari && firmano.length) who += '<span class="wholine">' + T.signers + firmano.map(label).join(", ") + "</span>";
  var title = opts.it ? s.titolo_it : s.titolo, ins = opts.it ? s.istruzioni_it : s.istruzioni;
  var links = (s.link || []).map(function (l) {
    var extra = (l.requisiti ? esc(l.requisiti) : "") + (l.requisiti && !l.verificato ? ". " : "") + (!l.verificato ? '<span class="unc">' + T.unconf + "</span>" : "");
    return '<li class="lk' + (l.tipo === "servizio_online" ? " lk-online" : "") + '"><a href="' + esc(l.url) + '" target="_blank" rel="noopener noreferrer"><span class="lkk">' + T.lk[l.tipo] + '</span><span class="lkl">' + esc(l.etichetta) + "</span></a>" + (extra ? "<small>" + extra + "</small>" : "") + "</li>";
  }).join("");
  var fonti = (s.fonti || []).map(function (f) {
    return '<li><a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.url.replace(/^https:\/\/(www\.)?/, "").split("/")[0]) + "</a> · " + esc(T.ftipo[f.tipo] || f.tipo) + ": " + esc(f.cosa_dice) + (f.consultata ? " (" + T.checked + esc(fmtDate(f.consultata, opts.lang)) + ")" : "") + "</li>";
  }).join("");
  var office = s.ufficio_suggerito ? '<p class="hint" style="margin:0"><b>' + T.officeHere + "</b>" + esc(s.ufficio_suggerito.nome + ", " + s.ufficio_suggerito.indirizzo) + "</p>" : "";
  var right = opts.op
    ? '<div class="qrbox"><span class="pill ' + (S.done[s.n] ? "p-o" : "p-v") + '">' + (S.done[s.n] ? "Fatto secondo il cittadino" : "Da fare") + '</span><span class="qrcode-txt">' + code + "</span></div>"
    : '<div class="qrbox"><div class="qr"><img src="/qr/' + plan.code + "/" + s.n + '.svg" alt="QR ' + code + '" width="116" height="116"></div><span class="qrcode-txt">' + code + "</span><small>" + esc(T.showAt + s.ufficio) + "</small></div>";
  var scan = opts.op && S.opStep === s.n;
  return '<li class="pstep' + (S.done[s.n] && !opts.op ? " done" : "") + (scan ? " scan" : "") + '"' + (scan ? ' id="scanned"' : "") + '><div class="pbody">'
    + (scan ? '<span class="scanlabel">QR scansionato a questo sportello</span>' : "")
    + '<div class="phead"><span class="num">' + s.n + '</span><div class="ptitle"><b dir="auto">' + esc(title) + "</b>" + who
    + dueHTML(s, plan, T, opts.op ? "it" : plan.lingua) + '<div class="badges">' + badges + "</div></div></div>"
    + (s.documenti_mancanti && s.documenti_mancanti.length ? '<span class="unc">' + T.missingDoc + esc(s.documenti_mancanti.map(function (d) { return opts.lang === "en" ? d.name_en : d.nome; }).join(", ")) + "</span>" : "")
    + '<ol class="ins" dir="auto">' + ins.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ol>"
    + '<div class="chan"><span class="pill ' + MODE_CLS[s.canale] + '">' + T.mode[s.canale] + "</span></div>" + office
    + (links ? '<ul class="links">' + links + "</ul>" : "")
    + (fonti ? '<details class="src"><summary>' + T.sources + " (" + s.fonti.length + ')</summary><ul>' + fonti + "</ul></details>" : "")
    + (opts.op ? "" : '<label class="donebox"><input type="checkbox" data-done="' + s.n + '"' + (S.done[s.n] ? " checked" : "") + "> " + T.done + "</label>")
    + "</div>" + right + "</li>";
}

function renderPlan() {
  var p = S.plan, T = TX[S.lang];
  $("plan").innerHTML = p.passi.map(function (s) { return stepHTML(s, p, {lang: S.lang}); }).join("");
  $("legend").innerHTML = "<span>" + T.legend + "</span>" + Object.keys(ST_CLS).map(function (k) { return '<span class="pill ' + ST_CLS[k] + '">' + T.st[k] + "</span>"; }).join("");
  $("planWho").textContent = T.who[p.scheda.nucleo] + " · " + T.arrival + " " + fmtDate(p.data_arrivo);
  $("planNote").textContent = p.nota_date;
  $("code").textContent = p.code;
  $("icsLink").href = "/api/plan/" + p.code + ".ics";
  $("pdfLink").href = "/api/plan/" + p.code + ".pdf";
  var u = p.ufficio_vicino;
  $("officePanel").hidden = !u;
  if (u) $("office").innerHTML = "<p style=\"margin:0\"><b>" + esc(u.nome) + "</b><br>" + esc(u.indirizzo) + "</p>"
    + '<p class="hint" style="margin:0">' + esc(String(u.distanza_km).replace(".", S.lang === "it" ? "," : ".")) + " " + T.km + esc(p.luogo ? p.luogo.nome : "") + "</p>"
    + '<p class="hint" style="margin:0">' + esc(u.orari) + "</p>"
    + (u.note ? '<p class="hint" style="margin:0">' + esc(u.note) + "</p>" : "")
    + '<p class="hint" style="margin:0">' + T.officeSrc + "ds549-sedi-dei-servizi-anagrafici</p>";
  var conf = p.punti_in_conflitto || [];
  $("conflictPanel").hidden = !conf.length;
  $("conflicts").innerHTML = conf.map(function (c) { return '<div class="conflict"><b>' + esc(c.tema) + "</b>" + c.fonti.map(function (f) { return "<span>" + esc(f) + "</span>"; }).join("") + "</div>"; }).join("");
  renderAnswers();
}

function renderAnswers() {
  var r = (S.plan && S.plan.risposte) || [], T = TX[S.lang];
  $("answersPanel").hidden = !r.length;
  $("answers").innerHTML = r.map(function (a) {
    return '<div class="lastq"><small>' + esc(a.domanda) + '</small><span dir="auto">' + esc(a.traduzione || a.risposta) + "</span>"
      + (a.traduzione ? '<small>' + esc(a.risposta) + "</small>" : "")
      + "<small>" + T.approved + esc(a.approvata) + " · " + T.sources + ": " + a.fonti.map(function (f) { return '<a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer">' + esc(f.url.replace(/^https:\/\/(www\.)?/, "").split("/")[0]) + "</a>"; }).join(", ") + "</small></div>";
  }).join("");
}

async function poll() {  // le risposte approvate allo sportello arrivano nel piano del cittadino
  if (!S.plan) return;
  var d = await api("/api/plan/" + S.plan.code);
  if (d.plan && d.plan.risposte.length !== S.plan.risposte.length) { S.plan.risposte = d.plan.risposte; renderAnswers(); }
}
setInterval(poll, 10000);

/* ---------------------------------------------------------------- voce: dettatura e lettura */

var SR = window.SpeechRecognition || window.webkitSpeechRecognition, rec = null, recOn = false, recBase = "";
function micUI() { $("micBtn").setAttribute("aria-pressed", String(recOn)); $("micTxt").textContent = recOn ? t("micStop") : t("mic"); }
function stopMic() { if (rec && recOn) { try { rec.stop(); } catch (e) { /* già fermo */ } } }
$("micBtn").addEventListener("click", function () {
  if (!SR) { status("status", t("noMic"), true); return; }
  if (recOn) { stopMic(); return; }
  try {
    rec = new SR(); rec.lang = $("micLang").value; rec.interimResults = true; rec.continuous = true;
    recBase = $("msg").value ? $("msg").value.replace(/\s*$/, " ") : "";
    rec.onresult = function (ev) { var s = ""; for (var i = 0; i < ev.results.length; i++) s += ev.results[i][0].transcript; $("msg").value = recBase + s; };
    rec.onerror = function (ev) { status("status", ev.error === "not-allowed" || ev.error === "service-not-allowed" ? t("micDenied") : t("noMic"), true); };
    rec.onend = function () { recOn = false; micUI(); };
    rec.start(); recOn = true; micUI(); status("status", t("listening"));
  } catch (e) { recOn = false; micUI(); status("status", t("micDenied"), true); }
});

function voiceLang() {
  var c = S.plan ? S.plan.lingua : (S.thread.filter(function (m) { return m.k === "card"; }).map(function (m) { return m.card.lingua; }).pop());
  return c || $("micLang").value || "it-IT";
}
function speak(text, btn) {
  if (!("speechSynthesis" in window)) { status("status", t("noTts"), true); return; }
  if (S.speaking) { speechSynthesis.cancel(); S.speaking = false; return; }
  var u = new SpeechSynthesisUtterance(text), lang = voiceLang();
  u.lang = lang; u.rate = 0.95;
  var v = speechSynthesis.getVoices().filter(function (x) { return x.lang.toLowerCase().replace("_", "-").indexOf(lang.slice(0, 2).toLowerCase()) === 0; });
  if (v.length) u.voice = v.filter(function (x) { return x.lang.toLowerCase().replace("_", "-") === lang.toLowerCase(); })[0] || v[0];
  u.onend = u.onerror = function () { S.speaking = false; };
  speechSynthesis.cancel(); speechSynthesis.speak(u); S.speaking = true;
}
$("listenBtn").addEventListener("click", function () {
  var last = S.thread.filter(function (m) { return m.k === "bot"; }).pop();
  if (last) speak(plain(last.text));
});
$("listenPlanBtn").addEventListener("click", function () {
  if (!S.plan) return;
  var p = S.plan;
  speak(p.passi.map(function (s) {
    var d = s.scadenza && s.scadenza.data ? ", " + fmtDate(s.scadenza.data, p.lingua) : "";
    return s.n + ". " + s.titolo + d + ". " + s.istruzioni.join(". ");
  }).join(". "));
});
if ("speechSynthesis" in window) speechSynthesis.getVoices();

/* ---------------------------------------------------------------- accessibilità */

$("bigBtn").addEventListener("click", function () {
  var on = document.documentElement.classList.toggle("big");
  this.setAttribute("aria-pressed", String(on));
});
$("contrastBtn").addEventListener("click", function () {
  var on = document.documentElement.classList.toggle("contrast");
  this.setAttribute("aria-pressed", String(on));
});
document.querySelectorAll(".lbtn[data-lang]").forEach(function (b) {
  b.addEventListener("click", function () { S.lang = b.getAttribute("data-lang"); S.langTouched = true; renderStatic(); });
});

/* ---------------------------------------------------------------- sportello */

function show(v) {
  var cit = v === "cit";
  $("view-cit").hidden = !cit; $("view-op").hidden = cit;
  $("tab-cit").setAttribute("aria-selected", String(cit)); $("tab-op").setAttribute("aria-selected", String(!cit));
  document.documentElement.lang = cit ? S.lang : "it";
  if (!cit && S.plan && !$("opCode").value) $("opCode").value = S.plan.code;
  window.scrollTo(0, 0);
}
$("tab-cit").addEventListener("click", function () { show("cit"); });
$("tab-op").addEventListener("click", function () { show("op"); });

async function openCase() {
  var v = $("opCode").value.trim().toUpperCase();
  $("opErr").hidden = true;
  var d = await api("/api/plan/" + encodeURIComponent(v));
  if (d.error) { $("opErr").textContent = d.error; $("opErr").hidden = false; $("opCase").hidden = true; return; }
  S.op = d.plan; S.opStep = d.step;
  var p = S.op, T = TX.it;
  $("opCodeTxt").textContent = p.code;
  $("opProf").textContent = T.who[p.scheda.nucleo] + ": " + p.scheda.persone.map(function (x) { return x.profilo_nome || (T.cit[x.cittadinanza] || "?") + (x.motivo && x.cittadinanza === "extra" ? " " + T.mot[x.motivo] : ""); }).join("; ");
  $("opLang").textContent = (function () { try { return new Intl.DisplayNames(["it"], {type: "language"}).of(p.lingua); } catch (e) { return p.lingua; } })();
  $("opArr").textContent = fmtDate(p.data_arrivo, "it");
  $("opSum").hidden = !p.scheda.riassunto_it; $("opSumText").textContent = p.scheda.riassunto_it;
  $("opWarn").hidden = !p.avvisi.length; $("opWarnText").innerHTML = p.avvisi.map(esc).join("<br>");
  $("opPlan").innerHTML = p.passi.map(function (s) { return stepHTML(s, p, {lang: "it", it: true, op: true}); }).join("");
  $("opCase").hidden = false; $("opEmpty").hidden = true;
  var sc = $("scanned"); if (sc) sc.scrollIntoView({behavior: "smooth", block: "center"});
}
$("opOpen").addEventListener("click", openCase);
$("opCode").addEventListener("keydown", function (e) { if (e.key === "Enter") openCase(); });

async function askCounter(q) {
  if (!S.op) { status("opStatus", "Apri prima il percorso di un cittadino.", true); return; }
  $("opQ").value = q; $("draft").hidden = true; $("opOk").hidden = true;
  status("opStatus", "");
  $("opAsk").disabled = true; $("opAsk").textContent = TX.it.busyBtn;
  var stop = startWork("opWork", "sportello-" + S.op.code, "it");
  var d = await api("/api/counter/ask", {code: S.op.code, question: q});
  stop();
  $("opAsk").disabled = false; $("opAsk").textContent = "Chiedi a Claude";
  if (d.error) { status("opStatus", d.error, true); return; }
  status("opStatus", "");
  var dr = S.draft = d.draft; dr.domanda = q;
  $("draftText").value = dr.risposta;
  $("draftTr").value = dr.traduzione || ""; $("draftTr").hidden = $("draftTrLabel").hidden = !dr.traduzione;
  $("draftConf").hidden = !dr.conflitti.length;
  $("draftConf").innerHTML = "<b>Fonti in conflitto</b>" + dr.conflitti.map(function (c) { return "<span>" + esc(c.tema) + ": " + c.fonti.map(esc).join(" / ") + "</span>"; }).join("");
  $("draftSrc").innerHTML = dr.fonti.length ? '<ul class="links">' + dr.fonti.map(function (f) {
    return '<li class="lk"><a href="' + esc(f.url) + '" target="_blank" rel="noopener noreferrer"><span class="lkk">' + esc(f.procedure_id + " · " + (TX.it.ftipo[f.tipo] || f.tipo)) + '</span><span class="lkl">' + esc(f.cosa_dice) + "</span></a></li>";
  }).join("") + "</ul>" : (dr.senza_fonti ? '<p class="err">Bozza senza fonti dal catalogo: verifica prima di approvare.</p>' : "");
  $("draft").hidden = false;
}
$("opAsk").addEventListener("click", function () { var q = $("opQ").value.trim(); if (q) askCounter(q); });
document.querySelectorAll(".chip").forEach(function (c) { c.addEventListener("click", function () { askCounter(c.getAttribute("data-q")); }); });
$("opApprove").addEventListener("click", async function () {
  var dr = S.draft; if (!dr || !S.op) return;
  var d = await api("/api/counter/approve", {code: S.op.code, domanda: dr.domanda, risposta: $("draftText").value,
                                             traduzione: $("draftTr").hidden ? "" : $("draftTr").value, procedure_citate: dr.procedure_citate});
  if (d.error) { status("opStatus", d.error, true); return; }
  $("draft").hidden = true; $("opOk").hidden = false;
  if (S.plan && S.plan.code === S.op.code) { S.plan.risposte = d.risposte; renderAnswers(); }
});

/* ---------------------------------------------------------------- avanzamento durante l'attesa */

function startWork(boxId, key, lang) {
  var box = $(boxId), t0 = Date.now(), last = {fasi: [], tool: null}, stopped = false;
  function draw() {
    var T = TX[lang || S.lang], P = T.phases, done = last.fasi.slice();
    if (last.tool) done.pop();
    var items = ['<li class="' + (done.length || last.tool ? "ok" : "now") + '">' + P.start + "</li>"]
      .concat(done.map(function (f) { return '<li class="ok">' + esc(P[f] || f) + "</li>"; }))
      .concat(last.tool ? ['<li class="now">' + esc(P[last.tool] || last.tool) + "</li>"] : []);
    box.innerHTML = "<b>" + T.working + "</b><ol>" + items.join("") + "</ol><small>" + Math.round((Date.now() - t0) / 1000) + T.seconds + " · " + T.usually + "</small>";
  }
  box.hidden = false; draw();
  var timer = setInterval(async function () {
    if (stopped) return;
    var d = await api("/api/progress/" + encodeURIComponent(key));
    if (!stopped && d && d.attivo) last = d;
    if (!stopped) draw();
  }, 700);
  return function () { stopped = true; clearInterval(timer); box.hidden = true; box.innerHTML = ""; };
}
async function ensureSession() {
  if (S.sid) return;
  var d = await api("/api/session", {});
  if (d.session_id) S.sid = d.session_id;
}

/* ---------------------------------------------------------------- schede (ingresso senza chat) */

S.entry = "chat"; S.form = {nucleo: "single", persone: [{relazione: "self", minorenne: false, cittadinanza: "extra", motivo: "study", profilo: ""}]};
function setEntry(e) {
  S.entry = e;
  document.querySelectorAll("[data-entry]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-entry") === e)); });
  $("formPanel").hidden = e !== "form"; $("aiPanel").hidden = e === "form" && !S.thread.length;
  if (e === "form") renderForm();
}
function sel(name, opts, cur, attrs) {
  return '<select class="field" ' + (attrs || "") + ' data-f="' + name + '">' + opts.map(function (o) { return '<option value="' + esc(o[0]) + '"' + (o[0] === cur ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("") + "</select>";
}
function renderForm() {
  if (!S.opz) return;
  var T = TX[S.lang], F = S.form, h = "";
  h += '<div class="segs" role="group">' + ["single", "family", "group"].map(function (k) { return '<button class="seg" data-nucleo="' + k + '" aria-pressed="' + (F.nucleo === k) + '">' + esc(T.who[k]) + "</button>"; }).join("") + "</div>";
  h += F.persone.map(function (p, i) {
    var rels = i === 0 ? [["self", T.rel.self]] : (F.nucleo === "group" ? [["mate", T.rel.mate]] : [["partner", T.rel.partner], ["child", T.rel.child], ["relative", T.rel.relative]]);
    var profs = [["", T.choose]].concat(S.opz.profili.filter(function (x) { return !x.cittadinanza || x.cittadinanza === p.cittadinanza; }).map(function (x) { return [x.id, x.nome]; }));
    return '<div class="mrow" data-i="' + i + '"><b class="mname">' + esc(i === 0 ? T.rel.self : T.person + (i + 1)) + "</b>"
      + "<label>" + T.relL + sel("relazione", rels, p.relazione) + "</label>"
      + "<label>" + T.citL + sel("cittadinanza", [["ita", T.citS.ita], ["ue", T.citS.ue], ["extra", T.citS.extra]], p.cittadinanza) + "</label>"
      + "<label>" + T.motL + sel("motivo", [["work", T.motS.work], ["study", T.motS.study], ["family", T.motS.family], ["other", T.motS.other]], p.motivo) + "</label>"
      + "<label>" + T.sitL + sel("profilo", profs, p.profilo, 'style="max-width:320px"') + "</label>"
      + (i > 0 ? '<label class="mchk"><input type="checkbox" data-f="minorenne"' + (p.minorenne ? " checked" : "") + "> " + T.minorL + '</label><button class="mdel" data-del="' + i + '">' + T.remove + "</button>" : "") + "</div>";
  }).join("");
  if (F.nucleo !== "single") h += '<button class="btn-o2" id="addP" style="align-self:flex-start">' + T.addP + "</button>";
  h += '<div class="setup"><div class="fieldwrap"><label for="fArr">' + T.arrL + '</label><input id="fArr" class="field" type="date" value="' + esc(F.data_arrivo || "") + '"' + (F.notYet ? " disabled" : "") + "></div>"
    + '<label class="donebox"><input type="checkbox" id="fNotYet"' + (F.notYet ? " checked" : "") + "> " + T.notYet + "</label></div>";
  h += '<div class="fieldwrap"><label for="fNear">' + T.nearL + '</label><input id="fNear" class="field" list="luoghi" placeholder="' + esc(T.nearPh) + '" value="' + esc(F.vicino_a || "") + '"><datalist id="luoghi">'
    + S.opz.fermate.concat(S.opz.atenei).map(function (x) { return '<option value="' + esc(x) + '">'; }).join("") + "</datalist></div>";
  h += '<div class="fieldwrap"><label for="fLang">' + T.langPlan + '</label><select id="fLang" class="field sel">' + $("micLang").innerHTML + "</select></div>";
  h += "<fieldset class=\"tools\"><legend><b>" + T.toolsL + '</b></legend><div class="haslist">' + Object.keys(T.tools).map(function (k) { return '<label class="donebox"><input type="checkbox" data-tool="' + k + '"' + ((F.strumenti || {})[k] ? " checked" : "") + "> " + esc(T.tools[k]) + "</label>"; }).join("") + "</div></fieldset>";
  h += "<fieldset class=\"tools\"><legend><b>" + T.docsL + '</b></legend><div class="haslist">' + S.opz.documenti.map(function (d) { return '<label class="donebox"><input type="checkbox" data-doc="' + d.id + '"' + ((F.documenti || {})[d.id] ? " checked" : "") + "> " + esc(S.lang === "en" ? d.name_en : d.nome) + "</label>"; }).join("") + "</div></fieldset>";
  $("formBody").innerHTML = h;
  $("fLang").value = F.lingua || $("micLang").value;
}
function readForm() {  // conserva quello che la persona ha già scelto
  var F = S.form;
  document.querySelectorAll("#formBody [data-i]").forEach(function (row) {
    var p = F.persone[+row.getAttribute("data-i")];
    row.querySelectorAll("[data-f]").forEach(function (el) { p[el.getAttribute("data-f")] = el.type === "checkbox" ? el.checked : el.value; });
  });
  if ($("fArr")) { F.data_arrivo = $("fArr").value; F.notYet = $("fNotYet").checked; F.vicino_a = $("fNear").value.trim(); F.lingua = $("fLang").value; }
  F.strumenti = {}; document.querySelectorAll("#formBody [data-tool]").forEach(function (el) { F.strumenti[el.getAttribute("data-tool")] = el.checked; });
  F.documenti = {}; document.querySelectorAll("#formBody [data-doc]").forEach(function (el) { F.documenti[el.getAttribute("data-doc")] = el.checked; });
}
$("formBody").addEventListener("change", function () { readForm(); renderForm(); });
$("formBody").addEventListener("click", function (e) {
  var b = e.target.closest("[data-nucleo],[data-del],#addP"); if (!b) return;
  readForm();
  if (b.id === "addP") S.form.persone.push({relazione: S.form.nucleo === "group" ? "mate" : "partner", minorenne: false, cittadinanza: S.form.persone[0].cittadinanza, motivo: "family", profilo: ""});
  else if (b.hasAttribute("data-del")) S.form.persone.splice(+b.getAttribute("data-del"), 1);
  else { S.form.nucleo = b.getAttribute("data-nucleo"); if (S.form.nucleo === "single") S.form.persone = S.form.persone.slice(0, 1); else if (S.form.persone.length < 2) S.form.persone.push({relazione: S.form.nucleo === "group" ? "mate" : "partner", minorenne: false, cittadinanza: S.form.persone[0].cittadinanza, motivo: "family", profilo: ""}); }
  renderForm();
});
$("formBtn").addEventListener("click", async function () {
  readForm();
  var F = S.form, T = TX[S.lang];
  var scheda = {
    nucleo: F.nucleo,
    persone: F.persone.map(function (p, i) { return {relazione: i === 0 ? "self" : p.relazione, minorenne: i === 0 ? false : !!p.minorenne, cittadinanza: p.cittadinanza, motivo: p.motivo, profilo: p.profilo || null}; }),
    data_arrivo: F.notYet || !F.data_arrivo ? null : F.data_arrivo, gia_arrivato: F.notYet ? false : (F.data_arrivo ? true : null),
    lingua: F.lingua || "it-IT", strumenti: F.strumenti, documenti: F.documenti, vicino_a: F.vicino_a || null,
    riassunto_it: "Scheda compilata a mano: " + F.persone.map(function (p) { var x = S.opz.profili.filter(function (q) { return q.id === p.profilo; })[0]; return x ? x.nome : TX.it.citS[p.cittadinanza]; }).join("; ") + ".",
    domanda_chiarimento: null, messaggio: T.formMsg
  };
  status("formStatus", "");
  var d = await api("/api/scheda", {session_id: S.sid, scheda: scheda});
  if (d.error) { status("formStatus", d.error, true); return; }
  S.sid = d.session_id;
  push({k: "bot", text: T.formMsg}); push({k: "card", card: d.card});
  setEntry("chat"); $("thread").scrollIntoView({behavior: "smooth", block: "start"});
});
document.querySelectorAll("[data-entry]").forEach(function (b) { b.addEventListener("click", function () { setEntry(b.getAttribute("data-entry")); }); });
api("/api/opzioni").then(function (d) { if (!d.error) { S.opz = d; if (S.entry === "form") renderForm(); } });

/* ---------------------------------------------------------------- invia per email: il server non riceve indirizzi */

$("mailBtn").addEventListener("click", async function () {
  if (!S.plan) return;
  var T = TX[S.lang], name = S.plan.code + ".pdf", subject = T.mailSubject + " " + S.plan.code;
  try {
    var blob = await (await fetch("/api/plan/" + S.plan.code + ".pdf")).blob();
    var file = new File([blob], name, {type: "application/pdf"});
    if (navigator.canShare && navigator.canShare({files: [file]})) {  // condivisione di sistema con il PDF allegato
      await navigator.share({files: [file], title: subject, text: T.mailBody});
      return;
    }
    var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  } catch (e) { if (e && e.name === "AbortError") return; }
  window.location.href = "mailto:?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(T.mailBody + " " + T.mailAttach);
});

/* ---------------------------------------------------------------- avvio */

$("sendBtn").addEventListener("click", send);
$("msg").addEventListener("keydown", function (e) { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); send(); } });
$("msg").addEventListener("input", function () { status("status", ""); });
$("thread").addEventListener("click", function (e) { var b = e.target.closest("[data-confirm]"); if (b) confirmCard(+b.getAttribute("data-confirm")); });
$("plan").addEventListener("change", function (e) { var n = e.target.getAttribute("data-done"); if (n) { S.done[n] = e.target.checked; renderPlan(); } });
var navLang = Array.prototype.find.call($("micLang").options, function (o) { return o.value.slice(0, 2) === (navigator.language || "it").slice(0, 2); });
if (navLang) $("micLang").value = navLang.value;
renderStatic();
})();
