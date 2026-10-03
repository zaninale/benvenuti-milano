"""Benvenuti a Milano: app Flask con una sola pagina.

    python app.py      # poi apri http://localhost:5000

Stato solo in memoria (store.py): niente database, le conversazioni non vanno su disco.
"""
import io
import re
from datetime import date, datetime, timedelta, timezone

import segno
from flask import Flask, Response, abort, jsonify, render_template, request

import agent
import pdf
import store
import tools

app = Flask(__name__)
CODICE = re.compile(r"^(MI-[A-Z0-9]{4})(?:-(\d{1,2}))?$")


def _body() -> dict:
    return request.get_json(silent=True) or {}


def split_code(code: str) -> tuple[str, int | None]:
    """'mi-7k4q-3' -> ('MI-7K4Q', 3): il QR di un passo contiene codice e numero del passo."""
    m = CODICE.match((code or "").strip().upper())
    return (m.group(1), int(m.group(2)) if m.group(2) else None) if m else ("", None)


def public(plan: dict) -> dict:
    return {k: v for k, v in plan.items() if not k.startswith("_")}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(ok=True, modello=agent.MODEL, effort=agent.EFFORT, catalogo=tools.CAT.data["versione"],
                   procedure=len(tools.CAT.procs), open_data=tools.PROVENIENZA)


@app.post("/api/chat")
def chat():
    body = _body()
    message = (body.get("message") or "").strip()[:2000]
    if not message:
        return jsonify(error="Scrivi o detta un messaggio prima di inviare."), 400
    sid, session = store.get_session(body.get("session_id"))
    try:
        out = agent.chat(session, message)
    except agent.AgentError as e:
        return jsonify(session_id=sid, error=str(e)), 502
    if out["plan"]:
        out["plan"] = public(out["plan"])
    return jsonify(session_id=sid, **out)


@app.post("/api/session")
def new_session():
    """Id di sessione prima della prima domanda, così la pagina può seguire l'avanzamento."""
    sid, _ = store.get_session(_body().get("session_id"))
    return jsonify(session_id=sid)


@app.get("/api/progress/<key>")
def progress(key):
    """Fasi reali del lavoro di Claude (nomi dei tool), per la pagina durante l'attesa."""
    p = agent.PROGRESS.get(key)
    if not p:
        return jsonify(attivo=False)
    return jsonify(attivo=not p["finito"], step=p["step"], tool=p["tool"], fasi=p["fasi"],
                   secondi=round(agent.time.time() - p["started_at"]))


@app.get("/api/opzioni")
def opzioni():
    """Elenchi per le schede: profili e documenti dal catalogo, fermate (ds535) e atenei (ds94)."""
    return jsonify(
        profili=[{k: p[k] for k in ("id", "nome", "gruppo", "cittadinanza", "criteri")} for p in tools.CAT.profili.values()],
        documenti=[{k: d[k] for k in ("id", "nome", "name_en")} for d in tools.CAT.documenti.values()],
        fermate=sorted({s["nome"] for s in tools.DATA[tools.opendata.METRO]}),
        atenei=sorted({a["ateneo"].title() for a in tools.DATA[tools.opendata.ATENEI]}))


@app.post("/api/scheda")
def scheda():
    body = _body()
    sid, session = store.get_session(body.get("session_id"))
    r = tools.propose_from_form(body.get("scheda") or {}, session)
    if r.is_error:
        return jsonify(session_id=sid, error=r.content), 400
    return jsonify(session_id=sid, card=r.card)


@app.post("/api/confirm")
def confirm():
    sid, session = store.get_session(_body().get("session_id"))
    try:
        out = agent.confirm(session)
    except agent.AgentError as e:
        return jsonify(session_id=sid, error=str(e)), 502
    if out["plan"]:
        out["plan"] = public(out["plan"])
    elif not out["error"]:
        out["error"] = "Il piano non è stato creato. Riprova a premere Conferma."
    return jsonify(session_id=sid, **out)


@app.get("/api/plan/<path:code>")
def get_plan(code):
    ics, pdf_ = code.lower().endswith(".ics"), code.lower().endswith(".pdf")
    base, step = split_code(code[:-4] if ics or pdf_ else code)
    plan = store.get_plan(base)
    if not plan:
        return jsonify(error="Nessun percorso con questo codice. Controlla le lettere con il cittadino."), 404
    if step and not 1 <= step <= len(plan["passi"]):
        return jsonify(error=f"Il percorso ha {len(plan['passi'])} passi: controlla il numero dopo il codice."), 404
    if pdf_:
        return Response(pdf.make_pdf(plan), mimetype="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="{base}.pdf"'})
    if ics:
        return Response(make_ics(plan), mimetype="text/calendar",
                        headers={"Content-Disposition": f'attachment; filename="{base}.ics"'})
    return jsonify(plan=public(plan), step=step)


@app.get("/qr/<code>/<int:n>.svg")
def qr(code, n):
    plan = store.get_plan(code)
    if not plan or not 1 <= n <= len(plan["passi"]):
        abort(404)
    buf = io.BytesIO()
    segno.make(f"{plan['code']}-{n}", error="m").save(buf, kind="svg", scale=4, border=2, dark="#15202B")
    return Response(buf.getvalue(), mimetype="image/svg+xml")


@app.post("/api/counter/ask")
def counter_ask():
    body = _body()
    plan = store.get_plan(split_code(body.get("code", ""))[0])
    if not plan:
        return jsonify(error="Nessun percorso con questo codice."), 404
    question = (body.get("question") or "").strip()[:1000]
    if not question:
        return jsonify(error="Scrivi una domanda."), 400
    try:
        return jsonify(draft=agent.ask_counter(plan, question))
    except agent.AgentError as e:
        return jsonify(error=str(e)), 502


@app.post("/api/counter/approve")
def counter_approve():
    """L'operatore approva (o corregge) la bozza: solo ora la risposta arriva al cittadino."""
    body = _body()
    plan = store.get_plan(split_code(body.get("code", ""))[0])
    if not plan:
        return jsonify(error="Nessun percorso con questo codice."), 404
    risposta = (body.get("risposta") or "").strip()[:2000]
    if not risposta:
        return jsonify(error="La risposta è vuota."), 400
    citate = [pid for pid in body.get("procedure_citate") or [] if tools.CAT.get(pid)]
    fonti = [f for pid in citate for f in tools.CAT.get(pid)["fonti"]]  # le fonti le rimette il server
    plan["risposte"].append({"domanda": (body.get("domanda") or "")[:500], "risposta": risposta,
                             "traduzione": (body.get("traduzione") or "").strip()[:2000] or None,
                             "fonti": fonti, "approvata": datetime.now().strftime("%d/%m/%Y %H:%M")})
    return jsonify(ok=True, risposte=plan["risposte"])


# ---------------------------------------------------------------- calendario .ics (senza dati personali)

def _ics_text(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Righe .ics di al massimo 75 ottetti, senza spezzare i caratteri UTF-8."""
    b, out = line.encode("utf-8"), []
    while len(b) > 75:
        cut = 75
        while b[cut] & 0xC0 == 0x80:
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b" " + b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)


def make_ics(plan: dict) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Benvenuti a Milano//Claude Impact Lab//IT",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for s in plan["passi"]:
        d = s["scadenza"]["data"]
        if not d:
            continue
        giorno = date.fromisoformat(d)
        url = next((x["url"] for x in (s["link"] or s["fonti"])), "")
        desc = f"{s['titolo']}\n{s['scadenza']['regola']}\n{s['codice_passo']}\n{url}"
        lines += ["BEGIN:VEVENT", f"UID:{s['codice_passo']}@benvenuti-a-milano", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{giorno:%Y%m%d}", f"DTEND;VALUE=DATE:{giorno + timedelta(days=1):%Y%m%d}",
                  "SUMMARY:" + _ics_text(f"{s['titolo']} ({s['codice_passo']})"), "DESCRIPTION:" + _ics_text(desc)]
        if url:
            lines.append("URL:" + url)
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P2D", "DESCRIPTION:" + _ics_text(s["titolo"]),
                  "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(l) for l in lines) + "\r\n"


if __name__ == "__main__":
    print(f"Catalogo {tools.CAT.data['versione']}: {len(tools.CAT.procs)} procedure. Modello {agent.MODEL}.")
    print("Apri http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
