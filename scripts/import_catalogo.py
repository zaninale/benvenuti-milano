"""Converte i contenuti di ArrivareMilano (profili, procedure, enti in YAML, verificati dal collega) nel
nostro schema e li unisce a data/procedures.yaml. Solo contenuti: nessun codice del collega.

    python scripts/import_catalogo.py C:\\Dev\\CLAUDE_IMPACT_LAB\\ArrivareMilano\\arrivare_milano\\data

Regole:
- le nostre voci hanno la precedenza: per una procedura in comune si aggiungono solo le fonti nuove;
- le voci importate conservano fonti, data e stato di verifica del collega ("da_verificare" resta tale);
- scadenza, dipende_da, canale, priorita e ambito si ricavano solo da frasi esplicite del testo;
  altrimenti scadenza nulla, canale da_verificare, priorita importante, ambito persona;
- le situazioni particolari diventano un solo passo che rimanda all'ente competente;
- i profili entrano nel catalogo con i loro criteri di scelta e l'elenco delle procedure.
Lo script si può rilanciare: prima toglie quello che aveva importato.
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "data" / "procedures.yaml"
ORIGINE = "ArrivareMilano"

# Profilo del collega -> tag dei nostri passi che valgono anche per lui (stessa situazione).
TAG_CATALOGO = {
    "italiano_da_altro_comune": ["ita_altro_comune"], "italiano_rientro_estero": [],
    "studente_italiano_fuori_sede": [], "ue_soggiorno_breve": [], "ue_lavoratore": ["ue"], "ue_studente": ["ue"],
    "ue_altro": ["ue"], "nonue_breve": [], "nonue_studente": ["extra_studio"],
    "nonue_lavoro_subordinato": ["extra_lavoro"], "nonue_lavoro_autonomo": [], "nonue_famiglia": ["extra_familiare"],
    "nonue_permesso_altro_stato_ue": [], "situazione_particolare": [],
}
CITTADINANZA = {"italiani": "ita", "ue": "ue", "non_ue": "extra", "particolari": None}
PERMESSO = {"nonue_studente": "PERM_S", "nonue_lavoro_subordinato": "PERM_L", "nonue_famiglia": "FAM"}
SANITA = {"nonue_studente": "SSN_S", "nonue_lavoro_subordinato": "SSN_L"}


def in_comune(pid: str, prof: dict) -> list[str] | None:
    """Procedura del collega che abbiamo già: i nostri id per questo profilo, oppure None."""
    gruppo, profilo = prof["gruppo"], prof["id"]
    fissi = {"contratto_soggiorno_sui": ["SUI"], "codice_fiscale": ["CF"], "residenza_cambio_anpr": ["RES_I"],
             "medico_cambio": ["SSN_I"]}
    if pid in fissi:
        return fissi[pid]
    if pid == "carta_identita":
        return ["T_ID_I"] if gruppo == "italiani" else ["T_ID_X"]
    if pid == "residenza_stranieri_estero":
        return ["RES_U"] if gruppo == "ue" else ["RES_S"] if profilo == "nonue_studente" else ["RES_X"]
    if pid in ("permesso_soggiorno_kit", "permesso_soggiorno_questura") and profilo in PERMESSO:
        return [PERMESSO[profilo]]  # la Questura è già un passo delle nostre istruzioni sul permesso
    if pid == "permesso_soggiorno_questura":
        return ["PERMESSO_SOGGIORNO_KIT"]  # unita al kit importato
    if pid == "assistenza_sanitaria":
        return ["SSN_U"] if gruppo == "ue" else [SANITA[profilo]] if profilo in SANITA else None
    return None


def tipo_fonte(url: str) -> str:
    ufficiali = ("comune.milano.it", ".gov.it", "europa.eu", "esteri.it", "poliziadistato.it", "regione.lombardia.it",
                 "portaleimmigrazione.it", "anagrafenazionale.interno.it")
    if any(d in url for d in ufficiali):
        return "ufficiale"
    return "istituzionale" if "yesmilano.it" in url else "secondaria"


def frasi(testo: str) -> list[str]:
    return [f.strip().rstrip(".") for f in re.split(r"(?<=[.;])\s+", " ".join((testo or "").split())) if f.strip()]


def scadenza(testo: str | None) -> dict | None:
    """Solo "Entro N giorni (lavorativi) dall'ingresso/arrivo": l'unica base che il codice sa calcolare."""
    m = re.search(r"[Ee]ntro (\d+) giorni( lavorativi)? dall'(ingresso|arrivo)", testo or "")
    if not m:
        return None
    return {"quantita": int(m.group(1)), "unita": "giorni_lavorativi" if m.group(2) else "giorni",
            "natura": "scadenza_di_legge", "base": "data_di_arrivo"}


def canale(src: dict) -> str:
    online = bool(re.search(r"\bonline\b", src.get("sintesi") or ""))
    if src.get("presenza"):
        return "online_o_di_persona" if online else "di_persona"
    return "online" if online else "da_verificare"


def converti(src: dict, nuovo_id: str, enti: dict, profili: list[str], dipende: list[str]) -> dict:
    ente = enti.get(src.get("ente")) or {}
    ver = src.get("verifica") or {}
    data = str(ver["data"]) if ver.get("data") else None
    fonti = [{"url": f["url"], "tipo": tipo_fonte(f["url"]), "cosa_dice": f["titolo"], "consultata": data}
             for f in src.get("fonti") or []]
    if ver.get("stato") == "verificato":
        stato = "fonte_ufficiale" if any(f["tipo"] != "secondaria" for f in fonti) else "fonte_secondaria"
    else:
        stato = "da_verificare"
    istruzioni = frasi(src.get("sintesi"))
    if src.get("documenti"):
        istruzioni.append("Documenti: " + "; ".join(src["documenti"]))
    if src.get("costi"):
        istruzioni.append("Costi: " + src["costi"].rstrip("."))
    if src.get("presenza"):
        istruzioni.append("Dove: " + src["presenza"].rstrip("."))
    sc = scadenza(src.get("scadenza"))
    if src.get("scadenza") and not sc:
        istruzioni.append("Scadenza: " + src["scadenza"].rstrip("."))
    if src.get("note"):
        istruzioni += frasi(src["note"])
    ch = canale(src)
    link = []
    if src.get("online"):
        link.append({"tipo": "servizio_online" if ch in ("online", "online_o_di_persona") else "informazioni",
                     "etichetta": src["online"]["etichetta"], "url": src["online"]["url"], "requisiti": None,
                     "verificato": ver.get("stato") == "verificato"})
    voce = {"id": nuovo_id, "titolo": src["titolo"], "ente": ente.get("nome") or "Informazioni",
            "ufficio": ente.get("nome") or "Nessuno sportello: informazioni da sapere", "ambito": "persona",
            "si_applica_a": profili, "dipende_da": dipende, "scadenza": sc, "priorita": "importante", "canale": ch,
            "stato_verifica": stato, "fase": src.get("fase"), "istruzioni": istruzioni, "link": link,
            "fonti": fonti, "importata_da": ORIGINE}
    if src.get("note_verifica"):
        voce["note_verifica"] = " ".join(src["note_verifica"].split())
    return voce


def situazione_particolare(prof: dict) -> dict:
    """Un solo passo che rimanda all'ente competente."""
    link = [{"tipo": "informazioni", "etichetta": l["titolo"], "url": l["url"], "requisiti": None, "verificato": False}
            for l in prof.get("link_utili") or []]
    fonti = [{"url": l["url"], "tipo": tipo_fonte(l["url"]), "cosa_dice": l["titolo"], "consultata": None}
             for l in prof.get("link_utili") or []]
    return {"id": "SITUAZIONE_PARTICOLARE", "titolo": "Rivolgiti all'ente competente per la tua situazione",
            "ente": "Questura, Prefettura o servizio di orientamento",
            "ufficio": "Questura di Milano, Prefettura di Milano o un servizio di orientamento per stranieri",
            "ambito": "persona", "si_applica_a": [prof["id"]], "dipende_da": [], "scadenza": None,
            "priorita": "importante", "canale": "da_verificare", "stato_verifica": "da_verificare", "fase": "arrivo",
            "istruzioni": [prof["nome"] + ": " + prof["descrizione"].rstrip(".")]
                          + [" ".join(a.split()) for a in prof.get("avvisi") or []],
            "link": link, "fonti": fonti, "importata_da": ORIGINE}


def main(sorgente: pathlib.Path) -> None:
    leggi = lambda nome: yaml.safe_load((sorgente / nome).read_text(encoding="utf-8"))  # noqa: E731
    procedure, prof_src, uffici = leggi("procedure.yaml"), leggi("profili.yaml"), leggi("uffici.yaml")
    enti = {u["id"]: u for u in uffici}
    sue = {p["id"]: p for p in procedure}
    gruppi = {g["id"]: g["nome"] for g in prof_src["gruppi"]}

    cat = yaml.safe_load(CATALOGO.read_text(encoding="utf-8"))
    cat["procedure"] = [p for p in cat["procedure"] if p.get("importata_da") != ORIGINE]
    nostre = {p["id"]: p for p in cat["procedure"]}

    profili, nuove, per_nuova = [], {}, {}
    for prof in prof_src["profili"]:
        ids, facoltative, note = [], [], {}
        voci = [{"id": v} if isinstance(v, str) else v for v in prof["procedure"]]
        if prof["gruppo"] == "particolari":
            voci = []  # un solo passo, sotto
        for v in voci:
            comuni = in_comune(v["id"], prof)
            if comuni is None:
                comuni = [v["id"].upper()]
                per_nuova.setdefault(v["id"].upper(), (v["id"], []))[1].append(prof["id"])
            for nid in comuni:
                if nid in nostre:  # le nostre voci hanno la precedenza: solo le fonti nuove
                    urls = {f["url"] for f in nostre[nid]["fonti"]}
                    ver = sue[v["id"]].get("verifica") or {}
                    for f in sue[v["id"]].get("fonti") or []:
                        if f["url"] not in urls:
                            nostre[nid]["fonti"].append({"url": f["url"], "tipo": tipo_fonte(f["url"]),
                                                         "cosa_dice": f["titolo"],
                                                         "consultata": str(ver["data"]) if ver.get("data") else None})
                            urls.add(f["url"])
                if nid not in ids:
                    ids.append(nid)
                if v.get("facoltativa"):
                    facoltative.append(nid)
                if v.get("nota"):
                    note[nid] = v["nota"]
        if prof["gruppo"] == "particolari":
            nuove["SITUAZIONE_PARTICOLARE"] = situazione_particolare(prof)
            ids = ["SITUAZIONE_PARTICOLARE"]
        profili.append({"id": prof["id"], "gruppo": gruppi[prof["gruppo"]], "cittadinanza": CITTADINANZA[prof["gruppo"]],
                        "nome": prof["nome"], "criteri": prof["descrizione"], "tag_catalogo": TAG_CATALOGO[prof["id"]],
                        "procedure": ids, "facoltative": facoltative, "note": note,
                        "avvisi": [" ".join(a.split()) for a in prof.get("avvisi") or []], "importato_da": ORIGINE})

    # Dipendenze solo da frasi esplicite: chi "prima di chiedere il visto" o "con il nulla osta" viene prima del visto.
    prima_del_visto = [nid for nid, (sid, _) in per_nuova.items()
                       if re.search(r"prima di chiedere il visto|[Cc]on il nulla osta", sue[sid].get("sintesi") or "")]
    for nid, (sid, prof_ids) in per_nuova.items():
        src = dict(sue[sid])
        dip = []
        if re.search(r"iscrizione anagrafica", src.get("sintesi") or ""):
            dip.append("residenza")
        if sid == "visto_ingresso" and prima_del_visto:
            dip.append(" o ".join(prima_del_visto))
        if sid == "permesso_soggiorno_kit":  # il passo in Questura del collega diventa parte del kit
            q = sue["permesso_soggiorno_questura"]
            src["sintesi"] = (src.get("sintesi") or "") + " " + q["sintesi"]
            src["fonti"] = src["fonti"] + [f for f in q["fonti"] if f["url"] not in {x["url"] for x in src["fonti"]}]
        nuove[nid] = converti(src, nid, enti, prof_ids, dip)
    cat["procedure"] += list(nuove.values())
    cat["profili"] = profili
    cat["importazione"] = {"origine": ORIGINE + " (documento di lavoro del collega, verificato il 2026-10-03)",
                           "procedure_importate": len(nuove), "profili": len(profili)}
    CATALOGO.write_text(yaml.safe_dump(cat, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8")
    print(f"Importate {len(nuove)} procedure e {len(profili)} profili: {', '.join(nuove)}")


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]))
