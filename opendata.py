"""Open data del Comune di Milano (API CKAN, nessuna chiave).

    python opendata.py      # scarica i tre dataset in data/cache/ e aggiorna la copia di riserva

All'avvio l'app legge data/cache/ (fuori dal repo). Se manca, usa la copia di riserva ridotta in
data/opendata/ (nel repo), così la demo funziona anche offline. Scarica solo se mancano entrambe.
"""
import csv
import io
import json
import pathlib
import urllib.parse
import urllib.request
from datetime import date

API = "https://dati.comune.milano.it/api/3/action/"
ROOT = pathlib.Path(__file__).parent
CACHE = ROOT / "data" / "cache"
RISERVA = ROOT / "data" / "opendata"

UFFICI = "ds549-sedi-dei-servizi-anagrafici"
METRO = "ds535_atm-fermate-linee-metropolitane"
ATENEI = "ds94-infogeo-atenei-sedi-localizzazione"


def _csv_url(slug: str) -> str:
    url = API + "package_show?" + urllib.parse.urlencode({"id": slug})
    with urllib.request.urlopen(url, timeout=30) as resp:
        resources = json.load(resp)["result"]["resources"]
    for r in resources:
        if (r.get("format") or "").upper() == "CSV":
            return r["url"]
    raise RuntimeError(f"Nessun CSV nel dataset {slug}")


def download(slug: str) -> pathlib.Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / f"{slug}.csv"
    with urllib.request.urlopen(_csv_url(slug), timeout=60) as resp:
        target.write_bytes(resp.read())
    return target


def _rows(path: pathlib.Path) -> list[dict]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(text), delimiter=";"))


def _coord(row: dict) -> tuple[float, float] | None:
    try:
        return float(row["LAT_Y_4326"]), float(row["LONG_X_4326"])
    except (KeyError, TypeError, ValueError):
        return None


def _riduci(slug: str, rows: list[dict]) -> list[dict]:
    """Tiene solo le colonne che servono, con coordinate valide."""
    out = []
    if slug == UFFICI:
        for i, r in enumerate(rows, 1):
            c = _coord(r)
            if c:
                nome = r["titolo"].strip() or "Sede dei servizi anagrafici"
                out.append({"id": f"ANA{i:02d}", "nome": nome, "indirizzo": r["Indirizzo"].strip(),
                            "orari": (r.get("orari") or "").strip(), "note": (r.get("Note") or "").strip()[:240],
                            "quartiere": (r.get("NIL") or "").strip(), "lat": c[0], "lon": c[1]})
    elif slug == METRO:
        per_nome = {}
        for r in rows:
            c = _coord(r)
            nome = (r.get("nome") or "").strip()
            if not c or not nome:
                continue
            if nome in per_nome:
                linee = set(per_nome[nome]["linee"].split(", ")) | {r["linee"].strip()}
                per_nome[nome]["linee"] = ", ".join(sorted(linee))
            else:
                per_nome[nome] = {"nome": nome, "linee": r["linee"].strip(), "lat": c[0], "lon": c[1]}
        out = list(per_nome.values())
    elif slug == ATENEI:
        visti = set()
        for r in rows:
            c = _coord(r)
            chiave = (r["DENOMINAZ"].strip(), r["INDIRIZZO"].strip())
            if c and chiave not in visti:
                visti.add(chiave)
                out.append({"ateneo": r["DENOMINAZ"].strip(), "indirizzo": r["INDIRIZZO"].strip(),
                            "facolta": (r.get("FACOLTA") or "").strip(), "quartiere": (r.get("NIL") or "").strip(),
                            "lat": c[0], "lon": c[1]})
    return out


def salva_riserva(slug: str, righe: list[dict]) -> None:
    RISERVA.mkdir(parents=True, exist_ok=True)
    payload = {"dataset": slug, "url": f"https://dati.comune.milano.it/dataset/{slug}",
               "scaricato": date.today().isoformat(), "righe": righe}
    (RISERVA / f"{slug}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def load(slug: str) -> tuple[list[dict], str]:
    """Restituisce (righe ridotte, provenienza): cache, poi copia di riserva, poi download."""
    cache = CACHE / f"{slug}.csv"
    if cache.exists():
        return _riduci(slug, _rows(cache)), "cache"
    riserva = RISERVA / f"{slug}.json"
    if riserva.exists():
        return json.loads(riserva.read_text(encoding="utf-8"))["righe"], "copia di riserva"
    return _riduci(slug, _rows(download(slug))), "download"


if __name__ == "__main__":
    for slug in (UFFICI, METRO, ATENEI):
        righe = _riduci(slug, _rows(download(slug)))
        salva_riserva(slug, righe)
        print(f"{slug}: {len(righe)} righe")
