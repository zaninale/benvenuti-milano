"""Tool degli agenti: tutti deterministici, nessun dato personale.

- get_catalog, compute_deadline, find_offices leggono il catalogo e gli open data del Comune.
- propose_profile e submit_plan ricevono le proposte di Claude: il server le controlla e, per il
  piano, calcola le date e aggiunge link e fonti presi dal catalogo (Claude non scrive date né URL).
- draft_answer riceve la bozza dell'agente sportello e le aggiunge le fonti del catalogo.
"""
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from difflib import get_close_matches

import catalog
import opendata
import store

CAT = catalog.load()
DATA, PROVENIENZA = {}, {}
for _slug in (opendata.UFFICI, opendata.METRO, opendata.ATENEI):
    DATA[_slug], PROVENIENZA[_slug] = opendata.load(_slug)


@dataclass
class Result:
    content: str                # testo per Claude (tool_result)
    is_error: bool = False
    terminal: bool = False      # chiude il turno: la risposta torna alla pagina
    message: str | None = None  # messaggio per la persona, scritto da Claude
    card: dict | None = None
    plan: dict | None = None
    draft: dict | None = None


def ok(obj, **kw) -> Result:
    return Result(json.dumps(obj, ensure_ascii=False), **kw)


def err(text: str) -> Result:
    return Result(text, is_error=True)


def parse_date(s) -> date | None:
    try:
        return date.fromisoformat(str(s))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- date (le calcola il codice)

FESTIVI = {(1, 1), (1, 6), (4, 25), (5, 1), (6, 2), (8, 15), (11, 1), (12, 7), (12, 8), (12, 25), (12, 26)}
# (12, 7): Sant'Ambrogio, patrono di Milano, uffici comunali chiusi


def pasqua(anno: int) -> date:
    """Domenica di Pasqua (algoritmo di Meeus/Jones/Butcher)."""
    a, b, c = anno % 19, anno // 100, anno % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mese = (h + l - 7 * m + 114) // 31
    giorno = (h + l - 7 * m + 114) % 31 + 1
    return date(anno, mese, giorno)


def non_lavorativo(d: date) -> bool:
    return d.weekday() >= 5 or (d.month, d.day) in FESTIVI or d == pasqua(d.year) + timedelta(days=1)


def piu_giorni_lavorativi(inizio: date, n: int) -> date:
    d, contati = inizio, 0
    while contati < n:
        d += timedelta(days=1)
        if not non_lavorativo(d):
            contati += 1
    return d


def deadline(pid: str, arrivo: date, residenza: date | None = None) -> dict:
    s = CAT.get(pid).get("scadenza")
    if not s:
        return {"data": None, "natura": None, "regola": None}
    unita = "giorni lavorativi" if s["unita"] == "giorni_lavorativi" else "giorni"
    da = "dall'arrivo" if s["base"] == "data_di_arrivo" else "dalla dichiarazione di residenza"
    out = {"data": None, "natura": s["natura"], "regola": f"{s['quantita']} {unita} {da}"}
    base = arrivo if s["base"] == "data_di_arrivo" else residenza
    if base is None:
        out["nota"] = "serve la data della dichiarazione di residenza"
        return out
    if s["unita"] == "giorni_lavorativi":
        out["data"] = piu_giorni_lavorativi(base, s["quantita"]).isoformat()
    else:
        out["data"] = (base + timedelta(days=s["quantita"])).isoformat()
    return out


NOTA_DATE = ("Date calcolate dal codice a partire dalla data di arrivo. I giorni lavorativi escludono sabati, "
             "domeniche e festivi, compreso Sant'Ambrogio. La verifica della dimora parte dalla scadenza della "
             "dichiarazione di residenza.")


def compute_deadline(args: dict, session: dict | None = None) -> Result:
    pid = args.get("procedure_id")
    if not CAT.get(pid):
        return err(f"procedure_id inesistente: {pid}. Usa un id restituito da get_catalog.")
    arrivo = parse_date(args.get("arrival_date"))
    if not arrivo:
        return err("arrival_date deve essere una data YYYY-MM-DD.")
    residenza = parse_date(args.get("residence_date"))
    return ok({"procedure_id": pid, **deadline(pid, arrivo, residenza), "come": NOTA_DATE})


# ---------------------------------------------------------------- catalogo

STRUMENTI_TAG = {"senza_email": "email", "senza_telefono": "telefono", "senza_sim_italiana": "sim_italiana",
                 "senza_dispositivo": "dispositivo", "senza_spid_cie": "spid_cie"}
STRANIERI_TAG = {"ue", "extra_lavoro", "extra_studio", "extra_familiare", "minore_extra", "nucleo_misto_estero"}


def _sito(url: str) -> str:
    return re.sub(r"^https://(www\.)?", "", url).split("/")[0]


def compact(p: dict) -> dict:
    """La voce di catalogo come la vede Claude: tutti i fatti, ma niente URL (li aggiunge il server)."""
    s = p.get("scadenza")
    out = {k: p[k] for k in ("id", "titolo", "ente", "ufficio", "ambito", "si_applica_a", "dipende_da",
                             "priorita", "canale", "stato_verifica", "istruzioni")}
    out["scadenza"] = deadline(p["id"], date(2000, 1, 1))["regola"] if s else None
    out["natura_scadenza"] = s["natura"] if s else None
    if p.get("firmatari"):
        out["firmatari"] = p["firmatari"]
    if p.get("strumento"):
        out["strumento"] = p["strumento"]["necessita"]
    out["link"] = [{"tipo": l["tipo"], "etichetta": l["etichetta"], "requisiti": l.get("requisiti"),
                    "verificato": l.get("verificato")} for l in p.get("link") or []]
    out["fonti"] = [{"tipo": f["tipo"], "sito": _sito(f["url"]), "cosa_dice": f["cosa_dice"]} for f in p["fonti"]]
    for k in ("fase", "note_verifica"):  # voci importate dal catalogo del collega
        if p.get(k):
            out[k] = p[k]
    return out


def expand(profile_ids: set[str]) -> set[str]:
    """Un profilo del catalogo porta con sé i tag dei nostri passi che valgono per la sua situazione."""
    tags = set(profile_ids)
    for pid in profile_ids & set(CAT.profili):
        tags |= set(CAT.profili[pid]["tag_catalogo"])
    return tags


def select(profile_ids: set[str]) -> list[dict]:
    profili = [CAT.profili[p] for p in profile_ids if p in CAT.profili]
    elencate = {pid for prof in profili for pid in prof["procedure"]}
    profile_ids = expand(profile_ids)
    italiano = "ita_altro_comune" in profile_ids or any(p["cittadinanza"] == "ita" for p in profili)
    straniero = bool(profile_ids & STRANIERI_TAG) or any(p["cittadinanza"] in ("ue", "extra") for p in profili)
    mancano = {STRUMENTI_TAG[t] for t in profile_ids if t in STRUMENTI_TAG}
    scelte = []
    for p in CAT.data["procedure"]:
        if p["id"] in elencate:
            scelte.append(p)
            continue
        for entry in p["si_applica_a"]:
            key, _ = catalog.split_entry(entry)
            if key in catalog.PROFILI and (key == "tutti" or key in profile_ids):
                scelte.append(p)
                break
            if key in catalog.STRUMENTI:
                tool, chi = catalog.STRUMENTI[key]
                if tool in mancano and (chi == "tutti" or (chi == "italiani" and italiano)
                                        or (chi == "stranieri" and straniero)):
                    scelte.append(p)
                    break
    return scelte


def get_catalog(args: dict, session: dict | None = None) -> Result:
    ids = set(args.get("profile_ids") or [])
    sconosciuti = ids - catalog.PROFILI - set(STRUMENTI_TAG) - set(CAT.profili)
    if sconosciuti:
        return err(f"profile_ids sconosciuti: {sorted(sconosciuti)}. Validi: {PROFILE_IDS}")
    scelte = select(ids)
    per_titolo = {}
    for p in scelte:
        per_titolo.setdefault(p["titolo"], []).append(p["id"])
    profili = {pid: {k: CAT.profili[pid][k] for k in ("nome", "procedure", "facoltative", "note", "avvisi")}
               for pid in sorted(ids & set(CAT.profili))}
    return ok({
        "profili": profili,
        "regole_nucleo": CAT.data["regole_nucleo"],
        "regole_strumenti": CAT.data["regole_strumenti"],
        "punti_in_conflitto": CAT.data["punti_in_conflitto"],
        "procedure": [compact(p) for p in scelte],
        "varianti_della_stessa_pratica": [v for v in per_titolo.values() if len(v) > 1],
        "documenti": [{k: d[k] for k in ("id", "nome", "ottenuto_con", "richiesto_da")} for d in CAT.documenti.values()],
        "nota": "Catalogo verificato il " + str(CAT.data["versione"]) + ". Le date le calcola il server; "
                "link e fonti complete li aggiunge il server al piano.",
    })


# ---------------------------------------------------------------- uffici vicini (open data)

PAROLE_VUOTE = set("""metro metropolitana fermata stazione station estacao estacion gare mm m1 m2 m3 m4 m5 linea
line linha vicino vicina perto cerca near pres proche da de di del della do dos das a al alla the in em en
zona area quartiere bairro barrio abito moro vivo live lives habito habite habita sede campus universita
university universidade universidad""".split())
ALIAS_ATENEI = {"polimi": "politecnico", "statale": "universita degli studi di milano", "unimi":
                "universita degli studi di milano", "bicocca": "bicocca", "bocconi": "bocconi",
                "cattolica": "cattolica"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def resolve_place(near: str) -> dict | None:
    m = re.match(r"^\s*(-?\d{1,2}\.\d+)\s*[,; ]\s*(-?\d{1,3}\.\d+)\s*$", near or "")
    if m:
        lat, lon = float(m.group(1)), float(m.group(2))
        if 45.3 < lat < 45.6 and 9.0 < lon < 9.4:
            return {"tipo": "coordinate", "nome": f"{lat:.4f}, {lon:.4f}", "lat": lat, "lon": lon}
        return None
    q = norm(near)
    for alias, full in ALIAS_ATENEI.items():
        q = re.sub(rf"\b{alias}\b", full, q)
    parole = [w for w in q.split() if w not in PAROLE_VUOTE]
    testo = " " + " ".join(parole) + " "
    # 1. fermata della metro contenuta nel testo (la più lunga vince)
    fermate = sorted(DATA[opendata.METRO], key=lambda s: -len(s["nome"]))
    for s in fermate:
        if f" {norm(s['nome'])} " in testo:
            return {"tipo": "fermata metro", "nome": s["nome"], "linee": s["linee"], "lat": s["lat"],
                    "lon": s["lon"], "fonte": opendata.METRO}
    # 2. sede universitaria: più parole in comune con ateneo, indirizzo, quartiere
    best, punti = None, 0
    for a in DATA[opendata.ATENEI]:
        campo = set(norm(f"{a['ateneo']} {a['indirizzo']} {a['quartiere']}").split())
        p = sum(1 for w in parole if len(w) >= 3 and w in campo)
        if p > punti:
            best, punti = a, p
    if best:
        return {"tipo": "sede universitaria", "nome": f"{best['ateneo'].title()}, {best['indirizzo'].title()}",
                "lat": best["lat"], "lon": best["lon"], "fonte": opendata.ATENEI}
    # 3. fermata con nome simile (errori di battitura)
    nomi = {norm(s["nome"]): s for s in fermate}
    simili = get_close_matches(" ".join(parole), list(nomi), n=1, cutoff=0.75)
    if simili:
        s = nomi[simili[0]]
        return {"tipo": "fermata metro", "nome": s["nome"], "linee": s["linee"], "lat": s["lat"],
                "lon": s["lon"], "fonte": opendata.METRO}
    return None


def nearest_offices(lat: float, lon: float, n: int = 3) -> list[dict]:
    uffici = [{k: u[k] for k in ("id", "nome", "indirizzo", "orari", "note", "quartiere", "lat", "lon")}
              | {"distanza_km": round(km(lat, lon, u["lat"], u["lon"]), 1)} for u in DATA[opendata.UFFICI]]
    return sorted(uffici, key=lambda u: u["distanza_km"])[:n]


def find_offices(args: dict, session: dict | None = None) -> Result:
    luogo = resolve_place(args.get("near", ""))
    if not luogo:
        return err("Luogo non trovato negli open data. Chiedi una fermata della metropolitana (es. Piola, "
                   "Loreto) o una sede universitaria (es. Politecnico, Bicocca), mai un indirizzo esatto.")
    uffici = nearest_offices(luogo["lat"], luogo["lon"])
    if session is not None:
        session["luogo"], session["uffici"] = luogo, uffici
    return ok({"luogo": luogo, "uffici_anagrafe": [{k: u[k] for k in ("id", "nome", "indirizzo", "orari", "note",
                                                                         "distanza_km")} for u in uffici],
               "fonte": opendata.UFFICI, "nota": "Distanza in linea d'aria dal punto indicato."})


# ---------------------------------------------------------------- scheda profilo

MOTIVI = {"work": "extra_lavoro", "study": "extra_studio", "family": "extra_familiare"}
INDIRIZZO = re.compile(r"(?i)\b(via|viale|piazza|piazzale|corso|largo|rua|avenida|street|calle|rue)\b.*\d")


def propose_profile(args: dict, session: dict) -> Result:
    persone = args.get("persone") or []
    if not persone or persone[0].get("relazione") != "self":
        return err("La prima persona deve essere chi scrive, con relazione 'self'.")
    mancano = []
    if not parse_date(args.get("data_arrivo")) and args.get("gia_arrivato") is not False:
        mancano.append("data di arrivo")
    for i, p in enumerate(persone, 1):
        chi = "di chi scrive" if i == 1 else f"della persona {i}"
        if p.get("profilo") is None and not p.get("minorenne"):
            mancano.append(f"profilo {chi}")
        elif p.get("profilo"):
            p["profilo_nome"] = CAT.profili[p["profilo"]]["nome"]
        if p.get("cittadinanza") is None:
            mancano.append(f"cittadinanza {chi}")
        elif p["cittadinanza"] == "extra" and not p.get("minorenne") and p.get("motivo") is None:
            mancano.append(f"motivo dell'arrivo {chi}")
        if i > 1 and p.get("minorenne") is None:
            mancano.append(f"se la persona {i} è minorenne")
    nota = ""
    vicino = args.get("vicino_a")
    if vicino and INDIRIZZO.search(vicino):
        vicino, nota = None, " Non registrare indirizzi esatti: basta una fermata della metro o l'università."
    card = {
        "nucleo": args.get("nucleo") or "single",
        "persone": persone,
        "data_arrivo": args.get("data_arrivo") if parse_date(args.get("data_arrivo")) else None,
        "lingua": args.get("lingua") or "it",
        "strumenti": args.get("strumenti") or {},
        "documenti": args.get("documenti") or {},
        "gia_arrivato": args.get("gia_arrivato"),
        "vicino_a": vicino,
        "riassunto_it": args.get("riassunto_it") or "",
        "mancano": mancano,
        "completa": not mancano and not args.get("domanda_chiarimento"),
    }
    session["card"], session["confirmed"] = card, False
    if card["completa"]:
        stato = "completa: la persona la vede con il pulsante Conferma. Non costruire il piano prima della conferma."
    else:
        stato = f"parziale (mancano: {', '.join(mancano) or 'la risposta alla tua domanda'}): niente pulsante Conferma."
    return Result("Scheda mostrata alla persona, " + stato + nota, terminal=True, message=args.get("messaggio"),
                  card=card)


# ---------------------------------------------------------------- piano

def person_tags(p: dict, card: dict) -> set[str]:
    tags = {"tutti"}
    if p.get("profilo") in CAT.profili:
        tags |= expand({p["profilo"]})
    cit = p.get("cittadinanza")
    if p.get("minorenne"):
        tags.add("minori")
        if cit == "extra":
            tags.add("minore_extra")
    elif cit == "ita":
        tags.add("ita_altro_comune")
    elif cit == "ue":
        tags.add("ue")
    elif cit == "extra" and p.get("motivo") in MOTIVI:
        tags.add(MOTIVI[p["motivo"]])
    cits = {x.get("cittadinanza") for x in card["persone"]}
    if "ita" in cits and cits & {"ue", "extra"}:
        tags.add("nucleo_misto_estero")
    return tags


def applies(proc: dict, n: int, card: dict) -> tuple[bool | None, str | None]:
    """Il passo vale per la persona n della scheda? True, False o None (non si sa). Più eventuale condizione."""
    p = card["persone"][n - 1]
    if proc["id"] in (CAT.profili.get(p.get("profilo")) or {}).get("procedure", []):
        return True, None  # il profilo del catalogo elenca questo passo
    tags = person_tags(p, card)
    italiano = p.get("cittadinanza") == "ita"
    strumenti = (card.get("strumenti") or {}) if n == 1 else {}  # gli strumenti nella scheda sono di chi scrive
    incerto = False
    for entry in proc["si_applica_a"]:
        key, cond = catalog.split_entry(entry)
        if key in catalog.PROFILI:
            if key in tags:
                return True, cond
        elif key in catalog.STRUMENTI:
            tool, chi = catalog.STRUMENTI[key]
            if (chi == "italiani" and not italiano) or (chi == "stranieri" and italiano):
                continue
            ha = strumenti.get(tool)
            if ha is False:
                return True, cond
            if ha is None:
                incerto = True
        else:
            incerto = True
    return (None if incerto else False), None


def submit_plan(args: dict, session: dict) -> Result:
    card = session.get("card")
    if not card or not session.get("confirmed"):
        return err("La persona non ha ancora confermato la scheda profilo: aspetta la conferma.")
    if not session.get("catalog_seen"):
        return err("Chiama prima get_catalog e costruisci il piano sui suoi risultati.")
    posseduti = {k for k, v in (card.get("documenti") or {}).items() if v is True}
    mancanti = {k for k, v in (card.get("documenti") or {}).items() if v is False}
    gia_fatti = {pid: CAT.documenti[d]["nome"] for d in posseduti if d in CAT.documenti
                 for pid in CAT.documenti[d]["ottenuto_con"]}
    passi = [p for p in args.get("passi") or [] if p.get("procedure_id") not in gia_fatti]
    tolti = [f"{p.get('procedure_id')}: tolto dal piano, la persona ha già {gia_fatti[p.get('procedure_id')]}"
             for p in args.get("passi") or [] if p.get("procedure_id") in gia_fatti]
    if not passi:
        return err("Il piano è vuoto.")
    vuoti = [str(p.get("procedure_id")) for p in passi
             if not (p.get("titolo") or "").strip() or not [x for x in p.get("istruzioni") or [] if x.strip()]]
    if vuoti or len((args.get("messaggio") or "").strip()) < 20:
        return err("Piano incompleto: ogni passo deve avere titolo e istruzioni nella lingua della persona"
                   + (f" (mancano in: {', '.join(vuoti)})" if vuoti else "")
                   + " e il messaggio deve avere 2 o 3 frasi. Manda il piano completo, non una prova.")
    ids = [p.get("procedure_id") for p in passi]
    sconosciuti = [i for i in ids if not CAT.get(i)]
    if sconosciuti:
        return err(f"Id inesistenti nel catalogo: {', '.join(map(str, sconosciuti))}. "
                   "Usa solo id restituiti da get_catalog e richiama submit_plan.")
    pos = {}
    for i, pid in enumerate(ids):
        pos.setdefault(pid, []).append(i)
    errori = [f"{pid} (passo {i + 1}) dipende da {dep} (passo {j + 1}): {dep} deve venire prima"
              for i, pid in enumerate(ids) for dep in CAT.deps[pid] for j in pos.get(dep, []) if j > i]
    if errori:
        return err("Ordine non valido rispetto a dipende_da:\n- " + "\n- ".join(errori)
                   + "\nRiordina i passi e richiama submit_plan.")

    # Da qui in poi si accetta il piano: i dubbi diventano avvisi per lo sportello.
    avvisi, persone = list(tolti), len(card["persone"])
    tutti = list(range(1, persone + 1))
    arrivo = parse_date(card["data_arrivo"])
    res_id = next((i for i in ids if i in catalog.RESIDENZA), None)
    res_data = parse_date(deadline(res_id, arrivo)["data"]) if res_id else None
    uffici = {u["id"]: u for u in DATA[opendata.UFFICI]}
    code = store.new_code()
    steps, visti = [], set()
    for i, p in enumerate(passi):
        pid, proc = p["procedure_id"], CAT.get(p["procedure_id"])
        per_chi = sorted({x for x in p.get("per_chi") or [] if isinstance(x, int) and 1 <= x <= persone}) or [1]
        if proc["ambito"] != "persona":
            per_chi = tutti
        if (pid, tuple(per_chi)) in visti:
            avvisi.append(f"{pid}: passo ripetuto per le stesse persone, tenuto una volta sola")
            continue
        visti.add((pid, tuple(per_chi)))
        esiti = [(n, *applies(proc, n, card)) for n in (per_chi if proc["ambito"] == "persona" else tutti)]
        if proc["ambito"] == "persona":
            for n, esito, cond in esiti:
                if esito is False:
                    avvisi.append(f"{pid}: secondo la scheda non risulta applicabile alla persona {n}")
                elif esito is None:
                    avvisi.append(f"{pid}: applicabilità alla persona {n} da verificare")
        elif not any(e for _, e, _ in esiti):
            avvisi.append(f"{pid}: applicabilità al nucleo da verificare")
        for _, esito, cond in esiti:
            if esito and cond and cond.startswith("se "):
                avvisi.append(f"{pid}: vale {cond}, da confermare con la persona")
                break
        if "tutti" in proc["si_applica_a"]:
            for alt in CAT.data["procedure"]:
                if alt["id"] != pid and alt["titolo"] == proc["titolo"] and "tutti" not in alt["si_applica_a"] \
                        and any(applies(alt, n, card)[0] for n in tutti):
                    avvisi.append(f"{pid}: esiste la variante {alt['id']}, più specifica per il profilo")
        ufficio = None
        if p.get("ufficio_id"):
            ufficio = uffici.get(p["ufficio_id"])
            if not ufficio:
                avvisi.append(f"{pid}: ufficio {p['ufficio_id']} non trovato negli open data, ignorato")
        n = len(steps) + 1
        steps.append({
            "n": n, "codice_passo": f"{code}-{n}", "procedure_id": pid,
            "titolo": p.get("titolo") or proc["titolo"], "istruzioni": p.get("istruzioni") or proc["istruzioni"],
            "titolo_it": proc["titolo"], "istruzioni_it": proc["istruzioni"], "per_chi": per_chi,
            "ente": proc["ente"], "ufficio": proc["ufficio"], "ambito": proc["ambito"], "canale": proc["canale"],
            "priorita": proc["priorita"], "stato_verifica": proc["stato_verifica"],
            "firmatari": proc.get("firmatari"), "strumento": (proc.get("strumento") or {}).get("necessita"),
            "scadenza": deadline(pid, arrivo, res_data),
            "dopo": [], "link": proc["link"], "fonti": proc["fonti"],
            "documenti_mancanti": [{"nome": CAT.documenti[d]["nome"], "name_en": CAT.documenti[d]["name_en"]}
                                   for d in sorted(mancanti) if d in CAT.documenti
                                   and pid in CAT.documenti[d]["richiesto_da"]],
            "ufficio_suggerito": {k: ufficio[k] for k in ("id", "nome", "indirizzo", "orari")} if ufficio else None,
        })
    numero = {s["procedure_id"]: s["n"] for s in reversed(steps)}
    for s in steps:
        s["dopo"] = sorted({numero[d] for d in CAT.deps[s["procedure_id"]] if d in numero and numero[d] < s["n"]})
    vicini = session.get("uffici") or []
    plan = {
        "code": code, "creato": date.today().isoformat(), "lingua": card["lingua"], "scheda": card,
        "data_arrivo": card["data_arrivo"], "passi": steps, "luogo": session.get("luogo"),
        "ufficio_vicino": vicini[0] if vicini else None, "punti_in_conflitto": CAT.data["punti_in_conflitto"],
        "avvisi": avvisi, "nota_date": NOTA_DATE, "catalogo": CAT.data["versione"], "risposte": [],
    }
    store.save_plan(plan)
    session["plan_code"] = code
    sintesi = {"codice": code, "passi": [{"n": s["n"], "procedure_id": s["procedure_id"],
                                          "scadenza": s["scadenza"]["data"], "natura": s["scadenza"]["natura"],
                                          "stato_verifica": s["stato_verifica"]} for s in steps],
               "avvisi": avvisi}
    return Result("Piano registrato e mostrato alla persona: " + json.dumps(sintesi, ensure_ascii=False),
                  terminal=True, message=args.get("messaggio"), plan=plan)


# ---------------------------------------------------------------- bozza per lo sportello

def draft_answer(args: dict, session: dict | None = None) -> Result:
    citate = args.get("procedure_citate") or []
    sconosciute = [i for i in citate if not CAT.get(i)]
    if sconosciute:
        return err(f"Id inesistenti nel catalogo: {', '.join(sconosciute)}. Cita solo id del catalogo.")
    fonti = []
    for pid in citate:
        proc = CAT.get(pid)
        for f in proc["fonti"]:
            fonti.append({"procedure_id": pid, "stato_verifica": proc["stato_verifica"], **f})
    temi = " ".join(norm(t) for t in args.get("conflitti") or [])
    conflitti = [c for c in CAT.data["punti_in_conflitto"]
                 if any(w in temi for w in norm(c["tema"]).split() if len(w) > 4)]
    draft = {"risposta": args.get("risposta", ""), "traduzione": args.get("traduzione"),
             "procedure_citate": citate, "fonti": fonti, "conflitti": conflitti,
             "in_conflitto": [pid for pid in citate if CAT.get(pid)["stato_verifica"] == "fonti_in_conflitto"]}
    return Result("Bozza mostrata all'operatore, che la approva o la corregge.", terminal=True, draft=draft)


# ---------------------------------------------------------------- schemi per Claude

def _null(schema: dict) -> dict:
    return {"anyOf": [schema, {"type": "null"}]}


def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


CATALOG_PROFILES = sorted(CAT.profili)  # profili e criteri di scelta: dal catalogo, non scritti a mano
PROFILE_IDS = CATALOG_PROFILES + ["minori", "minore_extra"] + sorted(STRUMENTI_TAG)

T_GET_CATALOG = {
    "name": "get_catalog",
    "description": "Procedure del catalogo verificato che valgono per i profili indicati (id dei profili della "
                   "scheda; 'minori' e 'minore_extra' se ci sono minorenni; senza_* per gli strumenti che la "
                   "persona NON ha), con le note dei profili, le regole del nucleo e degli strumenti, i punti in "
                   "conflitto e le varianti della stessa pratica. È la sola fonte di fatti su pratiche, scadenze, "
                   "uffici e fonti.",
    "strict": True,
    "input_schema": _obj({"profile_ids": {"type": "array", "items": {"type": "string", "enum": PROFILE_IDS}}}),
}
T_COMPUTE_DEADLINE = {
    "name": "compute_deadline",
    "description": "Calcola la scadenza di una procedura del catalogo a partire dalla data di arrivo (giorni o "
                   "giorni lavorativi, come dice il catalogo). Usala invece di calcolare date a mente.",
    "strict": True,
    "input_schema": _obj({"arrival_date": {"type": "string", "format": "date"},
                          "procedure_id": {"type": "string"},
                          "residence_date": _null({"type": "string", "format": "date"})}),
}
T_FIND_OFFICES = {
    "name": "find_offices",
    "description": "I 3 uffici anagrafe del Comune più vicini (open data ds549), in linea d'aria. 'near' è una "
                   "fermata della metropolitana (ds535), una sede universitaria (ds94) o 'lat,lon'. Mai un "
                   "indirizzo esatto.",
    "strict": True,
    "input_schema": _obj({"near": {"type": "string"}}),
}
T_PROPOSE_PROFILE = {
    "name": "propose_profile",
    "description": "Mostra alla persona la scheda di chi si trasferisce, da confermare prima del piano. Chiude il "
                   "tuo turno: 'messaggio' è quello che la persona legge, nella sua lingua. Se manca un dato "
                   "necessario metti null nel campo e una sola domanda in domanda_chiarimento e nel messaggio.",
    # niente strict: l'API ammette al massimo 16 parametri nullable negli schemi strict; il server valida
    # comunque con lo stesso schema (schema_errors), come per le schede compilate a mano
    "strict": False,
    "input_schema": _obj({
        "nucleo": {"type": "string", "enum": ["single", "family", "group"]},
        "persone": {"type": "array", "items": _obj({
            "relazione": {"type": "string", "enum": ["self", "partner", "child", "relative", "mate"]},
            "profilo": _null({"type": "string", "enum": CATALOG_PROFILES}),
            "minorenne": _null({"type": "boolean"}),
            "cittadinanza": _null({"type": "string", "enum": ["ita", "ue", "extra"]}),
            "motivo": _null({"type": "string", "enum": ["work", "study", "family", "other"]}),
        })},
        "data_arrivo": _null({"type": "string", "format": "date"}),
        "gia_arrivato": _null({"type": "boolean", "description": "false se la persona non è ancora arrivata a Milano"}),
        "lingua": {"type": "string", "description": "Tag BCP-47 della lingua in cui scrive la persona, es. pt-BR"},
        "strumenti": _obj({k: _null({"type": "boolean"}) for k in
                           ("email", "telefono", "sim_italiana", "dispositivo", "spid_cie")}),
        "documenti": _obj({k: _null({"type": "boolean"}) for k in sorted(CAT.documenti)}),
        "vicino_a": _null({"type": "string", "description": "Fermata metro, quartiere o università. Mai un indirizzo."}),
        "riassunto_it": {"type": "string", "description": "Una frase in italiano per lo sportello: solo fatti utili "
                                                          "alle pratiche, niente nomi, documenti, indirizzi o salute."},
        "domanda_chiarimento": _null({"type": "string"}),
        "messaggio": {"type": "string"},
    }),
}
T_SUBMIT_PLAN = {
    "name": "submit_plan",
    "description": "Registra il piano dopo che la persona ha confermato la scheda. Per ogni passo: id del catalogo, "
                   "persone (numeri della scheda, 1 = chi scrive), titolo e istruzioni nella lingua della persona, "
                   "ufficio_id da find_offices solo per i passi all'anagrafe. Il server rifiuta id inesistenti e "
                   "ordini che non rispettano dipende_da; calcola le date e aggiunge link e fonti. Chiude il turno.",
    "strict": True,
    "input_schema": _obj({
        "passi": {"type": "array", "items": _obj({
            "procedure_id": {"type": "string"},
            "per_chi": {"type": "array", "items": {"type": "integer"}},
            "titolo": {"type": "string"},
            "istruzioni": {"type": "array", "items": {"type": "string"}},
            "ufficio_id": _null({"type": "string"}),
        })},
        "messaggio": {"type": "string", "description": "2-3 frasi nella lingua della persona, senza date."},
    }),
}
T_DRAFT_ANSWER = {
    "name": "draft_answer",
    "description": "Consegna all'operatore la bozza di risposta, che lui approva o corregge. Il server aggiunge le "
                   "fonti delle procedure citate e i punti in conflitto.",
    "strict": True,
    "input_schema": _obj({
        "risposta": {"type": "string", "description": "In italiano, per l'operatore."},
        "traduzione": _null({"type": "string", "description": "La stessa risposta nella lingua del cittadino."}),
        "procedure_citate": {"type": "array", "items": {"type": "string"}},
        "conflitti": {"type": "array", "items": {"type": "string"}},
    }),
}

CITIZEN_TOOLS = [T_GET_CATALOG, T_COMPUTE_DEADLINE, T_FIND_OFFICES, T_PROPOSE_PROFILE, T_SUBMIT_PLAN]
COUNTER_TOOLS = [T_GET_CATALOG, T_DRAFT_ANSWER]
HANDLERS = {"get_catalog": get_catalog, "compute_deadline": compute_deadline, "find_offices": find_offices,
            "propose_profile": lambda args, session: propose_from_form(args, session), "submit_plan": submit_plan, "draft_answer": draft_answer}


def run_tool(name: str, args: dict, session: dict) -> Result:
    fn = HANDLERS.get(name)
    if not fn:
        return err(f"Tool sconosciuto: {name}")
    try:
        return fn(args, session)
    except Exception as e:  # l'errore torna a Claude invece di far cadere la richiesta
        return err(f"Errore del tool {name}: {e}")


def schema_errors(value, schema: dict, path: str = "scheda") -> list[str]:
    """Controlla un valore con il sottoinsieme di JSON Schema usato negli schemi dei tool."""
    if "anyOf" in schema:
        return [] if any(not schema_errors(value, s, path) for s in schema["anyOf"]) else [f"{path}: valore non valido"]
    tipi = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int, "null": type(None)}
    t = schema.get("type")
    if t and not (isinstance(value, tipi[t]) and not (t == "integer" and isinstance(value, bool))):
        return [f"{path}: deve essere {t}"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{path}: valore non ammesso {value!r}"]
    if t == "string" and schema.get("format") == "date" and not parse_date(value):
        return [f"{path}: data non valida"]
    errori = []
    if t == "object":
        props = schema.get("properties", {})
        errori += [f"{path}.{k}: manca" for k in schema.get("required", []) if k not in value]
        errori += [f"{path}.{k}: campo non previsto" for k in value if k not in props]
        for k, v in value.items():
            if k in props:
                errori += schema_errors(v, props[k], f"{path}.{k}")
    if t == "array":
        for i, v in enumerate(value):
            errori += schema_errors(v, schema.get("items", {}), f"{path}[{i}]")
    return errori


def propose_from_form(scheda: dict, session: dict) -> Result:
    """Le schede compilate a mano producono la stessa scheda di propose_profile, validata dallo stesso schema."""
    errori = schema_errors(scheda, T_PROPOSE_PROFILE["input_schema"])
    if errori:
        return err("Scheda non valida: " + "; ".join(errori[:5]))
    return propose_profile(scheda, session)
