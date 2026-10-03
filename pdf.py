"""Il piano in PDF (fpdf2): solo il piano, le date, le fonti e i QR. Nessun dato personale."""
import io
import pathlib
from datetime import date

import segno
from fpdf import FPDF

FONT = pathlib.Path(r"C:\Windows\Fonts\arial.ttf")
FONT_B = pathlib.Path(r"C:\Windows\Fonts\arialbd.ttf")
L = {
    "it": {"code": "Codice del percorso", "arr": "Arrivo", "notyet": "non ancora arrivato", "due": "Scadenza",
           "office": "Ufficio", "status": "Affidabilità", "src": "Fonti", "near": "Anagrafe più vicina",
           "conf": "Dove le fonti non concordano", "after": "dopo il passo", "asap": "appena possibile",
           "foot": "Demo indipendente, non realizzata dal Comune di Milano. Conferma sempre sulle fonti indicate.",
           "st": {"fonte_ufficiale": "fonte ufficiale", "fonte_secondaria": "fonte secondaria",
                  "da_verificare": "da verificare", "fonti_in_conflitto": "fonti in conflitto"}},
    "en": {"code": "Journey code", "arr": "Arrival", "notyet": "not arrived yet", "due": "Deadline",
           "office": "Office", "status": "Reliability", "src": "Sources", "near": "Nearest registry office",
           "conf": "Where sources disagree", "after": "after step", "asap": "as soon as possible",
           "foot": "Independent demo, not made by the City of Milan. Always confirm on the sources listed.",
           "st": {"fonte_ufficiale": "official source", "fonte_secondaria": "secondary source",
                  "da_verificare": "to be verified", "fonti_in_conflitto": "conflicting sources"}},
}


def _data(iso: str | None) -> str:
    return date.fromisoformat(iso).strftime("%d/%m/%Y") if iso else ""


def make_pdf(plan: dict) -> bytes:
    t = L["it" if (plan.get("lingua") or "it").lower().startswith("it") else "en"]
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=15)
    if FONT.exists():  # font di sistema con gli accenti di tutte le lingue latine
        pdf.add_font("Testo", "", str(FONT))
        pdf.add_font("Testo", "B", str(FONT_B if FONT_B.exists() else FONT))
        fam, txt = "Testo", (lambda s: s)
    else:
        fam, txt = "Helvetica", (lambda s: s.encode("latin-1", "replace").decode("latin-1"))

    def riga(testo, size=10, bold=False, w=0, h=5):
        pdf.set_font(fam, "B" if bold else "", size)
        pdf.multi_cell(w, h, txt(testo), new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()
    riga("Benvenuti a Milano", 18, True, h=9)
    riga(f"{t['code']}: {plan['code']}    {t['arr']}: {_data(plan.get('data_arrivo')) or t['notyet']}", 11)
    riga(plan.get("nota_date") or "", 9)
    for s in plan["passi"]:
        if pdf.get_y() > 230:
            pdf.add_page()
        pdf.ln(3)
        y = pdf.get_y()
        qr = io.BytesIO()
        segno.make(s["codice_passo"], error="m").save(qr, kind="png", scale=4, border=1)
        qr.seek(0)
        pdf.image(qr, x=172, y=y, w=24)
        sc = s["scadenza"] or {}
        due = _data(sc.get("data")) or sc.get("regola") or (f"{t['after']} {max(s['dopo'])}" if s.get("dopo") else t["asap"])
        riga(f"{s['n']}. {s['titolo']}", 12, True, w=160, h=6)
        riga(f"{t['due']}: {due}    {t['office']}: {s['ufficio']}    {t['status']}: {t['st'][s['stato_verifica']]}", 9, w=160)
        for i in s["istruzioni"]:
            riga(f"- {i}", 10, w=160)
        for f in s["fonti"]:
            riga(f"{t['src']}: {f['cosa_dice']} - {f['url']}", 8, w=160, h=4)
        riga(s["codice_passo"], 8, w=160, h=4)
        pdf.set_y(max(pdf.get_y(), y + 26))
    u = plan.get("ufficio_vicino")
    if u:
        pdf.ln(4)
        riga(t["near"], 12, True, h=6)
        riga(f"{u['nome']}, {u['indirizzo']} ({u['distanza_km']} km). {u.get('orari', '')}", 10)
        riga("Open data: ds549-sedi-dei-servizi-anagrafici", 8, h=4)
    if plan.get("punti_in_conflitto"):
        pdf.ln(4)
        riga(t["conf"], 12, True, h=6)
        for c in plan["punti_in_conflitto"]:
            riga(f"{c['tema']}: " + " / ".join(c["fonti"]), 10)
    pdf.ln(4)
    riga(t["foot"], 8, h=4)
    return bytes(pdf.output())
