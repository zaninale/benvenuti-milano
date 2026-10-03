"""Test dal vivo su tre profili importati dal catalogo del collega (chiama Claude: parte solo con RUN_LIVE=1).

    $env:RUN_LIVE=1; python -m pytest -q tests/test_live_profili.py -s
"""
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

pytestmark = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="imposta RUN_LIVE=1 per chiamare Claude")

CASI = [  # casi inventati
    ("italiano_rientro_estero", {"RES_I"},
     "Ciao, sono italiano e torno a vivere in Italia dopo sei anni a Londra, dove ero iscritto all'AIRE. Sono "
     "arrivato a Milano il 1° ottobre, vivo da solo vicino alla fermata Loreto. Ho email, cellulare italiano e SPID.",
     "Ho la carta d'identità italiana, il codice fiscale, la tessera sanitaria, il contratto d'affitto e il contratto di lavoro."),
    ("ue_lavoratore", {"RES_U", "ATTESTAZIONE_SOGGIORNO_UE"},
     "Bonjour, je suis française et je suis arrivée à Milan le 29 septembre pour travailler comme salariée dans une "
     "entreprise, pour au moins deux ans. J'habite seule près du métro Porta Venezia. J'ai un e-mail et un "
     "téléphone français, mais pas de SPID ni de carte d'identité italienne.",
     "J'ai ma carte d'identité, la carte européenne TEAM, mon contrat de travail et un bail à mon nom. Je n'ai pas encore "
     "de code fiscal."),
    ("situazione_particolare", {"SITUAZIONE_PARTICOLARE"},
     "Hello, I am from Afghanistan. I arrived in Milan alone on 30 September and I have applied for international "
     "protection. I live near Loreto metro. I have a phone and email.",
     "I have my passport and the receipt of my protection request. I have no tax code, no health card and no lease."),
]


@pytest.mark.parametrize("profilo,attesi,messaggio,documenti", CASI, ids=[c[0] for c in CASI])
def test_profilo_dal_vivo(profilo, attesi, messaggio, documenti):
    import app
    import tools

    c = app.app.test_client()
    r = c.post("/api/chat", json={"message": messaggio}).get_json()
    print(f"\n[{profilo}] risposta:", r.get("reply"))
    assert not r.get("error"), r
    if not (r.get("card") or {}).get("completa"):  # domanda riassuntiva su strumenti e documenti
        r = c.post("/api/chat", json={"session_id": r["session_id"], "message": documenti}).get_json()
        print(f"[{profilo}] risposta:", r.get("reply"))
    card = r["card"]
    assert card and card["completa"], r
    assert card["persone"][0]["profilo"] == profilo
    r = c.post("/api/confirm", json={"session_id": r["session_id"]}).get_json()
    assert not r.get("error"), r
    ids = [s["procedure_id"] for s in r["plan"]["passi"]]
    print(f"[{profilo}] piano:", ids, "| avvisi:", r["plan"]["avvisi"])
    assert attesi <= set(ids) and all(tools.CAT.get(i) for i in ids)
    for i, pid in enumerate(ids):
        assert all(ids.index(d) < i for d in tools.CAT.deps[pid] if d in ids)
