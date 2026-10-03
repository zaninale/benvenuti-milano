"""Catalogo delle procedure (data/procedures.yaml): la sola fonte di fatti su pratiche, scadenze,
link e fonti. Viene caricato e validato all'avvio: se qualcosa non torna, l'app non parte.

Qui si traducono anche in regole i campi scritti in testo libero (si_applica_a, dipende_da).
"""
import pathlib
import re

import yaml

PATH = pathlib.Path(__file__).parent / "data" / "procedures.yaml"

UNITA = {"giorni", "giorni_lavorativi"}
BASI = {"data_di_arrivo", "dichiarazione_di_residenza"}
NATURE = {"scadenza_di_legge", "data_consigliata", "data_limite"}
STATI = {"fonte_ufficiale", "fonte_secondaria", "da_verificare", "fonti_in_conflitto"}
PRIORITA = {"urgente", "importante", "da_pianificare"}
CANALI = {"online", "online_o_di_persona", "di_persona", "nessuna_azione", "da_solo", "da_verificare"}
AMBITI = {"persona", "nucleo", "abitazione"}
TIPI_FONTE = {"ufficiale", "istituzionale", "secondaria", "link_da_confermare"}
TIPI_LINK = {"servizio_online", "informazioni", "strumento"}

# Profili del catalogo: prima parola di si_applica_a.
PROFILI = {"tutti", "ita_altro_comune", "ue", "extra_lavoro", "extra_studio", "extra_familiare",
           "nucleo_misto_estero", "minori", "minore_extra"}

# si_applica_a in testo libero per gli strumenti -> (strumento che manca, a chi vale)
STRUMENTI = {
    "chi non ha email": ("email", "tutti"),
    "chi non ha un numero": ("telefono", "tutti"),
    "stranieri senza sim italiana": ("sim_italiana", "stranieri"),
    "chi non ha un dispositivo": ("dispositivo", "tutti"),
    "italiani senza spid/cie": ("spid_cie", "italiani"),
    "stranieri senza spid/cie": ("spid_cie", "stranieri"),
}

RESIDENZA = ["RES_I", "RES_U", "RES_X", "RES_S"]
# dipende_da in testo libero -> procedure che, se sono nel piano, devono venire prima
DIPENDENZE = {
    "la dichiarazione di residenza": RESIDENZA,
    "residenza": RESIDENZA,
    "la residenza del minore": RESIDENZA,
    "codice fiscale disponibile": ["CF", "SUI", "PERM_S", "PERM_L", "FAM"],
}


class CatalogError(Exception):
    pass


def split_entry(text: str) -> tuple[str, str | None]:
    """'extra_studio (se intestatario)' -> ('extra_studio', 'se intestatario')."""
    t, cond = text.strip(), []
    m = re.search(r"\(([^)]*)\)", t)
    if m:
        cond.append(m.group(1).strip())
        t = (t[:m.start()] + t[m.end():]).strip()
    if "," in t:
        t, rest = t.split(",", 1)
        cond.append(rest.strip())
    return t.strip().lower(), "; ".join(cond) or None


class Catalog:
    def __init__(self, data: dict):
        self.data = data
        self.procs = {p["id"]: p for p in data["procedure"]}
        self.deps = {p["id"]: self._deps(p) for p in data["procedure"]}

    def _deps(self, proc: dict) -> list[str]:
        """Procedure che devono precedere questa, se presenti nel piano."""
        out = []
        for entry in proc.get("dipende_da") or []:
            if entry in DIPENDENZE:
                out += DIPENDENZE[entry]
            else:
                out += [x.strip() for x in entry.split(" o ")]
        return out

    def get(self, pid: str) -> dict | None:
        return self.procs.get(pid)


def validate(data: dict) -> tuple[list[str], list[str]]:
    """Restituisce (errori, avvisi). Gli errori bloccano l'avvio."""
    errors, warnings = [], []
    for key in ("regole_nucleo", "regole_strumenti", "punti_in_conflitto", "procedure"):
        if key not in data:
            errors.append(f"manca la sezione {key}")
    procs = data.get("procedure") or []
    ids = [p.get("id") for p in procs]
    for pid in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"id duplicato: {pid}")
    known = set(ids)
    for p in procs:
        pid = p.get("id", "?")
        for field in ("titolo", "ente", "ufficio", "ambito", "si_applica_a", "priorita", "canale",
                      "stato_verifica", "istruzioni", "link", "fonti"):
            if field not in p:
                errors.append(f"{pid}: manca il campo {field}")
        if p.get("ambito") not in AMBITI:
            errors.append(f"{pid}: ambito non valido {p.get('ambito')}")
        if p.get("priorita") not in PRIORITA:
            errors.append(f"{pid}: priorita non valida {p.get('priorita')}")
        if p.get("canale") not in CANALI:
            errors.append(f"{pid}: canale non valido {p.get('canale')}")
        if p.get("stato_verifica") not in STATI:
            errors.append(f"{pid}: stato_verifica non valido {p.get('stato_verifica')}")
        s = p.get("scadenza")
        if s is not None:
            if s.get("unita") not in UNITA or s.get("base") not in BASI or s.get("natura") not in NATURE \
                    or not isinstance(s.get("quantita"), int):
                errors.append(f"{pid}: scadenza non valida {s}")
        for entry in p.get("dipende_da") or []:
            if entry in DIPENDENZE:
                continue
            for x in entry.split(" o "):
                if x.strip() not in known:
                    errors.append(f"{pid}: dipende_da non riconosciuto '{entry}'")
        for entry in p.get("si_applica_a") or []:
            key, _ = split_entry(entry)
            if key not in PROFILI and key not in STRUMENTI:
                warnings.append(f"{pid}: si_applica_a non tradotto in regola '{entry}' (verrà accettato con avviso)")
        for link in p.get("link") or []:
            if link.get("tipo") not in TIPI_LINK or not str(link.get("url", "")).startswith("https://"):
                errors.append(f"{pid}: link non valido {link}")
        for fonte in p.get("fonti") or []:
            if fonte.get("tipo") not in TIPI_FONTE or not str(fonte.get("url", "")).startswith("https://") \
                    or not fonte.get("consultata"):
                errors.append(f"{pid}: fonte non valida {fonte}")
    return errors, warnings


def load(path: pathlib.Path = PATH) -> Catalog:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors, warnings = validate(data)
    for w in warnings:
        print("Avviso catalogo:", w)
    if errors:
        raise CatalogError("Catalogo non valido:\n- " + "\n- ".join(errors))
    return Catalog(data)
