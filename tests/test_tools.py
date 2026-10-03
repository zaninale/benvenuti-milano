"""Test dei tool deterministici, compreso il caso di accettazione di Ana (senza chiamare Claude)."""
import json
import pathlib
import sys
from datetime import date

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import catalog  # noqa: E402
import opendata  # noqa: E402
import store  # noqa: E402
import tools  # noqa: E402

# Ana (caso inventato): arrivata il 2/10, extra-UE per studio, numero brasiliano, senza SIM italiana,
# senza codice fiscale, senza SPID/CIE, abita vicino alla fermata Piola.
ANA = {
    "nucleo": "single",
    "persone": [{"relazione": "self", "minorenne": False, "cittadinanza": "extra", "motivo": "study",
                 "profilo": "nonue_studente"}],
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
    session["confirmed"] = session["catalog_seen"] = True
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
    r = tools.submit_plan({"passi": passi(ANA_PLAN, "ANA03"), "messaggio": "Il tuo piano è pronto: il passo più urgente è il permesso."}, session)
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
    r = tools.submit_plan({"passi": passi(["RES_S", "PERM_S"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, ana_session())
    assert r.is_error and "PERM_S deve venire prima" in r.content
    r = tools.submit_plan({"passi": passi(["PERM_S", "T_SIM", "CF"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, ana_session())
    assert r.is_error and "CF deve venire prima" in r.content


def test_piano_di_prova_rifiutato():
    vuoto = [{"procedure_id": "PERM_S", "per_chi": [1], "titolo": "Permesso", "istruzioni": [], "ufficio_id": None}]
    r = tools.submit_plan({"passi": vuoto, "messaggio": "x"}, ana_session())
    assert r.is_error and "PERM_S" in r.content


def test_id_inesistente_rifiutato():
    r = tools.submit_plan({"passi": passi(["PERM_S", "RES_Z"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, ana_session())
    assert r.is_error and "RES_Z" in r.content


def test_piano_senza_conferma_o_senza_catalogo_rifiutato():
    session = ana_session()
    session["confirmed"] = False
    assert tools.submit_plan({"passi": passi(["PERM_S"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, session).is_error
    session = ana_session()
    session["catalog_seen"] = False
    assert "get_catalog" in tools.submit_plan({"passi": passi(["PERM_S"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, session).content


def test_passo_non_applicabile_accettato_con_avviso():
    r = tools.submit_plan({"passi": passi(["PERM_S", "T_EMAIL", "SUI"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, ana_session())
    assert not r.is_error
    assert any(a.startswith("T_EMAIL: secondo la scheda non risulta applicabile") for a in r.plan["avvisi"])
    assert any(a.startswith("SUI: secondo la scheda non risulta applicabile") for a in r.plan["avvisi"])


def test_strumento_non_dichiarato_accettato_con_avviso():
    session = ana_session()
    session["card"]["strumenti"]["dispositivo"] = None
    r = tools.submit_plan({"passi": passi(["T_DEV"]), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, session)
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


# ---------------------------------------------------------------- i 14 profili del catalogo

def ordina(ids):
    from graphlib import TopologicalSorter
    return list(TopologicalSorter({i: [d for d in tools.CAT.deps[i] if d in ids] for i in ids}).static_order())


def test_quattordici_profili_dal_catalogo():
    import agent
    assert len(tools.CAT.profili) == 14
    schema = tools.T_PROPOSE_PROFILE["input_schema"]["properties"]["persone"]["items"]["properties"]["profilo"]
    assert schema["anyOf"][0]["enum"] == sorted(tools.CAT.profili)  # niente elenchi scritti a mano
    prompt = agent.system_prompt("agent_citizen.md")
    assert all(f"- {pid} (" in prompt and p["criteri"] in prompt for pid, p in tools.CAT.profili.items())


@pytest.mark.parametrize("pid", sorted(tools.CAT.profili))
def test_piano_per_ogni_profilo(pid):
    prof = tools.CAT.profili[pid]
    cit = prof["cittadinanza"] or "extra"
    persona = {"relazione": "self", "minorenne": False, "cittadinanza": cit,
               "motivo": "other" if cit == "extra" else None, "profilo": pid}
    session = {}
    r = tools.propose_profile(dict(ANA, persone=[persona]), session)
    assert r.card["completa"], r.card["mancano"]
    session["confirmed"] = session["catalog_seen"] = True
    trovate = {p["id"] for p in json.loads(tools.get_catalog({"profile_ids": [pid]}).content)["procedure"]}
    assert set(prof["procedure"]) <= trovate
    ids = ordina(prof["procedure"])
    r = tools.submit_plan({"passi": passi(ids), "messaggio": "Ecco il tuo piano, con i passi in ordine."}, session)
    assert not r.is_error, r.content
    fatti = [s["procedure_id"] for s in r.plan["passi"]]
    assert fatti == ids and all(tools.CAT.get(i) for i in fatti)
    for i, x in enumerate(fatti):
        assert all(fatti.index(d) < i for d in tools.CAT.deps[x] if d in fatti)
    assert not any("non risulta applicabile" in a for a in r.plan["avvisi"])


def test_situazione_particolare_un_solo_passo():
    assert tools.CAT.profili["situazione_particolare"]["procedure"] == ["SITUAZIONE_PARTICOLARE"]
    passo = tools.CAT.get("SITUAZIONE_PARTICOLARE")
    assert passo["stato_verifica"] == "da_verificare" and any("questure" in l["url"] for l in passo["link"])


def test_voci_importate_conservano_verifica_del_collega():
    for p in tools.CAT.data["procedure"]:
        if p.get("importata_da"):
            assert p["stato_verifica"] in ("fonte_ufficiale", "fonte_secondaria", "da_verificare")
            if p["stato_verifica"] == "da_verificare":
                assert p["scadenza"] is None or p["id"] == "DICHIARAZIONE_PRESENZA"
            assert p["fonti"] and p["priorita"] == "importante"


# ---------------------------------------------------------------- schede compilate a mano e documenti posseduti

def scheda_ana(**doc):
    documenti = {k: False for k in tools.CAT.documenti}
    documenti.update(passaporto=True, visto=True, iscrizione_o_lavoro=True, **doc)
    return {"nucleo": "single", "persone": [{"relazione": "self", "minorenne": False, "cittadinanza": "extra",
                                             "motivo": "study", "profilo": "nonue_studente"}],
            "data_arrivo": "2026-10-02", "gia_arrivato": True, "lingua": "pt-BR",
            "strumenti": {"email": True, "telefono": True, "sim_italiana": False, "dispositivo": True, "spid_cie": False},
            "documenti": documenti, "vicino_a": "PIOLA", "riassunto_it": "Scheda compilata a mano.",
            "domanda_chiarimento": None, "messaggio": "Ecco la tua scheda."}


def test_schede_producono_la_scheda_e_il_piano_di_ana():
    assert tools.schema_errors(scheda_ana(), tools.T_PROPOSE_PROFILE["input_schema"]) == []
    assert tools.propose_from_form(dict(scheda_ana(), nucleo="tribu"), {}).is_error
    session = {}
    r = tools.propose_from_form(scheda_ana(), session)
    assert not r.is_error and r.card["completa"] and r.card["documenti"]["passaporto"] is True
    session["confirmed"] = session["catalog_seen"] = True
    r = tools.submit_plan({"passi": passi(ANA_PLAN), "messaggio": "Il tuo piano è pronto, con i passi in ordine."},
                          session)
    assert not r.is_error and [s["procedure_id"] for s in r.plan["passi"]] == ANA_PLAN
    by = {s["procedure_id"]: s for s in r.plan["passi"]}
    assert any(d["nome"].startswith("Permesso") for d in by["RES_S"]["documenti_mancanti"])
    assert any(d["nome"] == "Codice fiscale" for d in by["T_SIM"]["documenti_mancanti"])


def test_codice_fiscale_gia_posseduto_niente_cf():
    session = {}
    tools.propose_from_form(scheda_ana(codice_fiscale=True), session)
    session["confirmed"] = session["catalog_seen"] = True
    r = tools.submit_plan({"passi": passi(ANA_PLAN), "messaggio": "Il tuo piano è pronto, con i passi in ordine."},
                          session)
    ids = [s["procedure_id"] for s in r.plan["passi"]]
    assert "CF" not in ids and len(ids) == 7
    assert any(a.startswith("CF: tolto dal piano") for a in r.plan["avvisi"])
    assert not {s["procedure_id"]: s for s in r.plan["passi"]}["T_SIM"]["documenti_mancanti"]


def test_non_ancora_arrivato():
    assert tools.propose_from_form(dict(scheda_ana(), data_arrivo=None, gia_arrivato=False), {}).card["completa"]


def test_endpoint_opzioni_e_scheda():
    import app
    c = app.app.test_client()
    o = c.get("/api/opzioni").get_json()
    assert len(o["profili"]) == 14 and "PIOLA" in o["fermate"] and len(o["documenti"]) == 7
    assert c.post("/api/scheda", json={"scheda": scheda_ana()}).get_json()["card"]["completa"]
    assert c.post("/api/scheda", json={"scheda": {"nucleo": "single"}}).status_code == 400


# ---------------------------------------------------------------- avanzamento durante l'attesa

def test_progress_segue_i_tool(monkeypatch):
    from types import SimpleNamespace as NS
    import agent
    import app
    import store
    risposte = iter([
        NS(stop_reason="tool_use", content=[NS(type="tool_use", id="t1", name="get_catalog",
                                                input={"profile_ids": ["nonue_studente"]})]),
        NS(stop_reason="end_turn", content=[NS(type="text", text="Fatto.")]),
    ])
    visto = []
    def finto(*a, **k):
        stato = agent.PROGRESS.get(sid) or {}
        visto.append(dict(stato, fasi=list(stato.get("fasi", []))))
        return next(risposte)
    monkeypatch.setattr(agent, "_call", finto)
    c = app.app.test_client()
    sid = c.post("/api/session", json={}).get_json()["session_id"]
    assert c.get(f"/api/progress/{sid}").get_json() == {"attivo": False}
    out = agent.run(store.get_session(sid)[1], "sistema", [], "ciao", 100)
    assert out["reply"] == "Fatto." and visto[1]["fasi"] == ["get_catalog"] and not visto[0]["fasi"]
    p = c.get(f"/api/progress/{sid}").get_json()
    assert p["attivo"] is False and p["fasi"] == ["get_catalog"] and p["step"] == 1


def test_pdf_del_piano_valido():
    import app
    session = ana_session()
    r = tools.submit_plan({"passi": passi(ANA_PLAN), "messaggio": "Il tuo piano è pronto, con i passi in ordine."},
                          session)
    res = app.app.test_client().get(f"/api/plan/{r.plan['code']}.pdf")
    assert res.status_code == 200 and res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF") and res.data.rstrip().endswith(b"%%EOF") and len(res.data) > 5000
