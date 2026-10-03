"""Test di accettazione dal vivo: chiama davvero Claude (costa crediti), quindi parte solo con RUN_LIVE=1.

    $env:RUN_LIVE=1; python -m pytest -q tests/test_live_ana.py -s
"""
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

pytestmark = pytest.mark.skipif(os.getenv("RUN_LIVE") != "1", reason="imposta RUN_LIVE=1 per chiamare Claude")

ANA_MSG = ("Olá! Sou brasileira e cheguei a Milão ontem, dia 2 de outubro, para fazer um mestrado no Politecnico, "
           "com visto de estudo. Moro sozinha num quarto perto da estação de metrô Piola. Tenho e-mail, "
           "smartphone e um número de celular brasileiro, mas ainda não tenho chip italiano, nem código fiscal, "
           "nem SPID.")
ANA_DOC = ("Tenho passaporte, visto de estudo e a matrícula no Politecnico. Ainda não tenho permesso di soggiorno "
           "nem recibo, nem código fiscal, nem cartão de saúde. O quarto é alugado com contrato no meu nome.")
ATTESI = ["PERM_S", "SSN_S", "CF", "T_SIM", "RES_S", "CHECK", "T_ID_X", "TARI_S"]


def test_ana_dalla_chat_al_piano():
    import app
    import catalog
    import tools

    c = app.app.test_client()
    r = c.post("/api/chat", json={"message": ANA_MSG}).get_json()
    print("\nRisposta:", r.get("reply"))
    assert not r.get("error"), r
    if not (r.get("card") or {}).get("completa"):  # domanda riassuntiva su strumenti e documenti
        r = c.post("/api/chat", json={"session_id": r["session_id"], "message": ANA_DOC}).get_json()
        print("Risposta:", r.get("reply"))
    card = r["card"]
    assert card and card["completa"], r
    p = card["persone"][0]
    assert (p["cittadinanza"], p["motivo"], card["data_arrivo"]) == ("extra", "study", "2026-10-02")
    assert card["lingua"].lower().startswith("pt")

    r = c.post("/api/confirm", json={"session_id": r["session_id"]}).get_json()
    print("Messaggio:", r.get("reply"))
    assert not r.get("error"), r
    plan = r["plan"]
    ids = [s["procedure_id"] for s in plan["passi"]]
    print("Piano:", ids, "\nAvvisi:", plan["avvisi"])
    assert sorted(ids) == sorted(ATTESI)
    for i, pid in enumerate(ids):  # ordine equivalente rispetto alle dipendenze
        assert all(ids.index(d) < i for d in tools.CAT.deps[pid] if d in ids)
    by = {s["procedure_id"]: s for s in plan["passi"]}
    assert by["PERM_S"]["scadenza"]["data"] == "2026-10-14"
    assert by["RES_S"]["scadenza"]["data"] == "2026-10-22"
    assert by["TARI_S"]["scadenza"]["data"] == "2026-12-31"
    assert {pid for pid in ids if by[pid]["stato_verifica"] == "fonti_in_conflitto"} == {"SSN_S", "CHECK", "T_ID_X"}
    assert plan["ufficio_vicino"]["id"] == "ANA03"
    for s in plan["passi"]:  # l'ufficio anagrafe solo nei passi che si fanno al Comune
        ufficio = (s["ufficio_suggerito"] or {}).get("nome")
        print(f"{s['n']}. {s['procedure_id']} {s['scadenza']['data']} | {s['titolo']} | {ufficio}")
        for riga in s["istruzioni"]:
            print("     -", riga)
        assert s["ufficio_suggerito"] is None or "Comune" in s["ufficio"]
    assert not any(pid in ids for pid in ("T_EMAIL", "T_PHONE", "TARI")) and "RES_S" in catalog.RESIDENZA


def test_ana_dalle_schede():
    import app
    from test_tools import scheda_ana

    c = app.app.test_client()
    r = c.post("/api/scheda", json={"scheda": scheda_ana()}).get_json()
    assert r["card"]["completa"]
    r = c.post("/api/confirm", json={"session_id": r["session_id"]}).get_json()
    assert not r.get("error"), r
    ids = [s["procedure_id"] for s in r["plan"]["passi"]]
    print("\nPiano dalle schede:", ids)
    assert sorted(ids) == sorted(ATTESI)
