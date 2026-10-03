"""Test dei tool deterministici, compreso il caso di accettazione di Ana (senza chiamare Claude)."""
import json
import pathlib
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import catalog  # noqa: E402
import opendata  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402

# Ana (caso inventato): arrivata il 2/10, extra-UE per studio, numero brasiliano, senza SIM italiana,
# senza codice fiscale, senza SPID/CIE, abita vicino alla fermata Piola.
ANA = {
    "nucleo": "single",
    "persone": [{"relazione": "self", "minorenne": False, "cittadinanza": "extra", "motivo": "study"}],
    "data_arrivo": "2026-10-02", "lingua": "pt-BR",
    "strumenti": {"email": True, "telefono": True, "sim_italiana": False, "dispositivo": True, "spid_cie": False},
    "vicino_a": "Piola", "riassunto_it": "Studentessa extra-UE, arrivata il 2/10, vive da sola.",
    "domanda_chiarimento": None, "messaggio": "Confira o seu perfil.",
}
ANA_PLAN = ["PERM_S", "SSN_S", "CF", "T_SIM", "RES_S", "CHECK", "T_ID_X", "TARI_S"]


def ana_session():
    session = {}
    r = tools.propose_profile(dict(ANA), session)
    assert r.terminal and r.card["completa"]
    session["confirmed"] = True
    tools.find_offices({"near": "Piola"}, session)
    return session


def passi(ids, ufficio=None):
    return [{"procedure_id": pid, "per_chi": [1], "titolo": f"titolo {pid}", "istruzioni": [f"passo {pid}"],
             "ufficio_id": ufficio if pid.startswith("RES") else None} for pid in ids]


def test_catalogo_valido_e_regole_tradotte():
    errori, avvisi = catalog.validate(tools.CAT.data)
    assert errori == []
    assert avvisi == []  # ogni si_applica_a in testo libero ha una regola nel codice


def test_open_data_caricati():
    assert len(tools.DATA[opendata.UFFICI]) >= 10
    assert any(s["nome"] == "PIOLA" for s in tools.DATA[opendata.METRO])
    assert any("POLITECNICO" in a["ateneo"] for a in tools.DATA[opendata.ATENEI])


def test_copia_di_riserva_nel_repo():
    for slug in (opendata.UFFICI, opendata.METRO, opendata.ATENEI):
        assert (opendata.RISERVA / f"{slug}.json").exists()


def test_scadenze_di_ana():
    arrivo = date(2026, 10, 2)
    assert tools.deadline("PERM_S", arrivo)["data"] == "2026-10-14"   # 8 giorni lavorativi
    assert tools.deadline("CF", arrivo)["data"] == "2026-10-16"       # 14 giorni
    assert tools.deadline("RES_S", arrivo)["data"] == "2026-10-22"    # 20 giorni
    assert tools.deadline("TARI_S", arrivo)["data"] == "2026-12-31"   # 90 giorni
    assert tools.deadline("SSN_S", arrivo)["data"] is None            # nessuna scadenza nel catalogo
    assert tools.deadline("CHECK", arrivo)["data"] is None            # serve la data della residenza
    assert tools.deadline("CHECK", arrivo, date(2026, 10, 22))["data"] == "2026-12-06"


def test_giorni_lavorativi_saltano_festivi():
    assert tools.pasqua(2026) == date(2026, 4, 5)
    # venerdì 4/12/2026: lunedì 7 (Sant'Ambrogio) e martedì 8 dicembre non contano
    assert tools.piu_giorni_lavorativi(date(2026, 12, 4), 8) == date(2026, 12, 18)
    # Pasquetta 2027 (29 marzo) non conta
    assert tools.piu_giorni_lavorativi(date(2027, 3, 26), 1) == date(2027, 3, 30)


def test_compute_deadline_tool():
    out = json.loads(tools.compute_deadline({"arrival_date": "2026-10-02", "procedure_id": "PERM_S",
                                             "residence_date": None}).content)
    assert out["data"] == "2026-10-14" and out["natura"] == "scadenza_di_legge"
    assert tools.compute_deadline({"arrival_date": "2026-10-02", "procedure_id": "XYZ"}).is_error


def test_find_offices_vicino_a_piola():
    out = json.loads(tools.find_offices({"near": "perto da estação Piola"}).content)
    assert out["luogo"]["nome"] == "PIOLA" and out["luogo"]["tipo"] == "fermata metro"
    d = [u["distanza_km"] for u in out["uffici_anagrafe"]]
    assert d == sorted(d) and d[0] < 3 and len(d) == 3


def test_find_offices_universita_e_coordinate():
    out = json.loads(tools.find_offices({"near": "Politecnico"}).content)
    assert out["luogo"]["tipo"] == "sede universitaria"
    out = json.loads(tools.find_offices({"near": "45.4811, 9.2259"}).content)
    assert out["luogo"]["tipo"] == "coordinate"
    assert tools.find_offices({"near": "Atlantide"}).is_error


def test_get_catalog_per_ana():
    out = json.loads(tools.get_catalog({"profile_ids": ["extra_studio", "senza_sim_italiana",
                                                        "senza_spid_cie"]}).content)
    ids = {p["id"] for p in out["procedure"]}
    assert ids == {"PERM_S", "CF", "RES_S", "CHECK", "SSN_S", "TARI", "TARI_S", "T_SIM", "T_ID_X"}
    assert ["TARI", "TARI_S"] in out["varianti_della_stessa_pratica"]
    assert "https://" not in json.dumps(out["procedure"])  # gli URL li aggiunge il server, non Claude
    assert tools.get_catalog({"profile_ids": ["marziano"]}).is_error


def test_piano_di_ana_accettato():
    session = ana_session()
    r = tools.submit_plan({"passi": passi(ANA_PLAN, "ANA03"), "messaggio": "Pronto"}, session)
    assert not r.is_error and r.terminal
    plan = r.plan
    assert [s["procedure_id"] for s in plan["passi"]] == ANA_PLAN
    by = {s["procedure_id"]: s for s in plan["passi"]}
    assert by["PERM_S"]["scadenza"]["data"] == "2026-10-14"
    assert by["RES_S"]["scadenza"]["data"] == "2026-10-22"
    assert by["TARI_S"]["scadenza"]["data"] == "2026-12-31"
    assert by["CHECK"]["scadenza"]["data"] == "2026-12-06"
    for pid in ("SSN_S", "CHECK", "T_ID_X"):
        assert by[pid]["stato_verifica"] == "fonti_in_conflitto"
    assert by["T_SIM"]["strumento"] == "consigliato" and 3 in by["T_SIM"]["dopo"]   # dopo il codice fiscale
    assert 5 in by["T_ID_X"]["dopo"]                                                # dopo la residenza
    assert by["PERM_S"]["link"][0]["url"].startswith("https://www.poste.it/")       # link dal catalogo
    assert by["RES_S"]["ufficio_suggerito"]["id"] == "ANA03"
    assert plan["ufficio_vicino"]["distanza_km"] < 3
    assert any(a.startswith("TARI_S: vale se intestatario") for a in plan["avvisi"])
    assert not any("non risulta applicabile" in a for a in plan["avvisi"])
    assert store.get_plan(plan["code"]) is plan
    assert "T_EMAIL" not in json.dumps(tools.get_catalog({"profile_ids": ["extra_studio", "senza_sim_italiana",
                                                                          "senza_spid_cie"]}).content)


def test_ordine_sbagliato_rifiutato():
    r = tools.submit_plan({"passi": passi(["RES_S", "PERM_S"]), "messaggio": ""}, ana_session())
    assert r.is_error and "PERM_S deve venire prima" in r.content
    r = tools.submit_plan({"passi": passi(["PERM_S", "T_SIM", "CF"]), "messaggio": ""}, ana_session())
    assert r.is_error and "CF deve venire prima" in r.content


def test_id_inesistente_rifiutato():
    r = tools.submit_plan({"passi": passi(["PERM_S", "RES_Z"]), "messaggio": ""}, ana_session())
    assert r.is_error and "RES_Z" in r.content


def test_piano_senza_conferma_rifiutato():
    session = ana_session()
    session["confirmed"] = False
    assert tools.submit_plan({"passi": passi(["PERM_S"]), "messaggio": ""}, session).is_error


def test_passo_non_applicabile_accettato_con_avviso():
    r = tools.submit_plan({"passi": passi(["PERM_S", "T_EMAIL", "SUI"]), "messaggio": ""}, ana_session())
    assert not r.is_error
    assert any(a.startswith("T_EMAIL: secondo la scheda non risulta applicabile") for a in r.plan["avvisi"])
    assert any(a.startswith("SUI: secondo la scheda non risulta applicabile") for a in r.plan["avvisi"])


def test_strumento_non_dichiarato_accettato_con_avviso():
    session = ana_session()
    session["card"]["strumenti"]["dispositivo"] = None
    r = tools.submit_plan({"passi": passi(["T_DEV"]), "messaggio": ""}, session)
    assert not r.is_error and any("da verificare" in a for a in r.plan["avvisi"])


def test_scheda_parziale_e_niente_indirizzi():
    session = {}
    args = dict(ANA, persone=[{"relazione": "self", "minorenne": False, "cittadinanza": None, "motivo": None}],
                vicino_a="Via Roma 12")
    r = tools.propose_profile(args, session)
    assert not r.card["completa"] and "cittadinanza di chi scrive" in r.card["mancano"]
    assert r.card["vicino_a"] is None
    assert tools.propose_profile(dict(ANA, persone=[]), {}).is_error


def test_bozza_sportello_con_fonti_e_conflitti():
    r = tools.draft_answer({"risposta": "L'importo è in conflitto.", "traduzione": None,
                            "procedure_citate": ["SSN_S"], "conflitti": ["Contributo SSN volontario studenti"]})
    assert r.terminal and r.draft["in_conflitto"] == ["SSN_S"]
    assert any("unive.it" in f["url"] for f in r.draft["fonti"])
    assert r.draft["conflitti"][0]["tema"].startswith("Contributo SSN")
    assert tools.draft_answer({"risposta": "", "procedure_citate": ["NOPE"], "conflitti": []}).is_error
