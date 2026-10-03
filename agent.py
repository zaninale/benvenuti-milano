"""Claude a runtime: l'agente del cittadino e quello dello sportello.

Schema di _hub/starter/runs_on_claude.py: tool use con al massimo 6 giri per richiesta.
La cronologia resta in memoria (store.py) e si allunga solo in coda. Quando Claude chiama un tool che
chiude il turno (propose_profile, submit_plan, draft_answer) la risposta torna subito alla pagina e il
tool_result parte con il messaggio successivo: una chiamata in meno a ogni passaggio.
"""
import json
import os
import pathlib
from datetime import date

import anthropic
from dotenv import load_dotenv

import tools

load_dotenv()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
EFFORT = os.getenv("AGENT_EFFORT", "low")  # non CLAUDE_EFFORT: può essere già impostata nel sistema
MAX_TURNS = 6
PROMPTS = pathlib.Path(__file__).parent / "prompts"
_client = None


class AgentError(Exception):
    """Errore da mostrare nella pagina, con un messaggio chiaro."""


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # legge ANTHROPIC_API_KEY da .env
    return _client


def system_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8") + f"\n\nOggi è {date.today().isoformat()}."


def _call(system: str, tool_list: list, messages: list, max_tokens: int):
    try:
        return client().messages.create(
            model=MODEL, max_tokens=max_tokens, system=system, tools=tool_list, messages=messages,
            thinking={"type": "adaptive"}, output_config={"effort": EFFORT},
        )
    except anthropic.AuthenticationError:
        raise AgentError("Chiave API Anthropic mancante o non valida: controlla il file .env.")
    except anthropic.RateLimitError:
        raise AgentError("Troppe richieste in poco tempo: attendi un momento e riprova.")
    except anthropic.APIConnectionError:
        raise AgentError("Claude non è raggiungibile: controlla la connessione e riprova.")
    except anthropic.APIStatusError as e:
        raise AgentError(f"Claude ha risposto con un errore ({e.status_code}). Riprova tra poco.")


def run(session: dict, system: str, tool_list: list, user_text: str, max_tokens: int, ctx=None) -> dict:
    messages = session["messages"]
    start, pending = len(messages), list(session.get("pending") or [])
    messages.append({"role": "user", "content": pending + [{"type": "text", "text": user_text}]})
    session["pending"] = []
    out = {"reply": "", "card": None, "plan": None, "draft": None, "error": None}
    try:
        for turn in range(MAX_TURNS):
            resp = _call(system, tool_list, messages, max_tokens)
            if resp.stop_reason == "refusal":
                raise AgentError("L'assistente non può rispondere a questa richiesta. Per le pratiche puoi "
                                 "rivolgerti allo sportello anagrafe del Comune.")
            messages.append({"role": "assistant", "content": resp.content})
            text = "".join(b.text for b in resp.content if b.type == "text").strip()
            if resp.stop_reason != "tool_use":
                out["reply"] = text
                if resp.stop_reason == "max_tokens":
                    out["error"] = "La risposta è stata interrotta perché troppo lunga."
                return out
            results, stop = [], None
            for b in resp.content:
                if b.type != "tool_use":
                    continue
                r = tools.run_tool(b.name, b.input, ctx if ctx is not None else session)
                print(f"  tool {b.name}: {'ERRORE ' + r.content[:200] if r.is_error else 'ok'}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": r.content,
                                "is_error": r.is_error})
                if r.terminal and not r.is_error:
                    stop = r
            if stop or turn == MAX_TURNS - 1:
                session["pending"] = results  # partiranno con il prossimo messaggio
                if stop:
                    out.update(reply=stop.message or text, card=stop.card, plan=stop.plan, draft=stop.draft)
                else:
                    out["error"] = "L'assistente ha fatto troppi passaggi. Riprova con un messaggio più semplice."
                return out
            messages.append({"role": "user", "content": results})
    except AgentError:
        del messages[start:]  # si torna allo stato di prima: la richiesta non è avvenuta
        session["pending"] = pending
        raise
    return out


def chat(session: dict, message: str) -> dict:
    return run(session, system_prompt("agent_citizen.md"), tools.CITIZEN_TOOLS, message, max_tokens=4000)


def confirm(session: dict) -> dict:
    card = session.get("card")
    if not card or not card.get("completa"):
        raise AgentError("Non c'è ancora una scheda completa da confermare.")
    session["confirmed"] = True
    text = "[Pulsante Conferma] Ho controllato la scheda e la confermo: prepara il mio piano."
    return run(session, system_prompt("agent_citizen.md"), tools.CITIZEN_TOOLS, text, max_tokens=8000)


def ask_counter(plan: dict, question: str) -> dict:
    """Nuova conversazione a ogni domanda: l'operatore riceve una bozza da approvare."""
    session = {"messages": [], "pending": []}
    contesto = {
        "codice": plan["code"], "lingua_cittadino": plan["lingua"], "data_arrivo": plan["data_arrivo"],
        "scheda": {k: plan["scheda"].get(k) for k in ("nucleo", "persone", "strumenti", "riassunto_it")},
        "passi": [{"n": s["n"], "procedure_id": s["procedure_id"], "titolo": s["titolo_it"],
                   "scadenza": s["scadenza"]["data"], "stato_verifica": s["stato_verifica"]} for s in plan["passi"]],
        "avvisi": plan["avvisi"],
    }
    text = ("Piano del cittadino:\n" + json.dumps(contesto, ensure_ascii=False)
            + "\n\nDomanda dell'operatore:\n" + question)
    out = run(session, system_prompt("agent_counter.md"), tools.COUNTER_TOOLS, text, max_tokens=4000, ctx=session)
    if out["draft"]:
        return out["draft"]
    return {"risposta": out["reply"] or out["error"] or "", "traduzione": None, "procedure_citate": [],
            "fonti": [], "conflitti": [], "in_conflitto": [], "senza_fonti": True}
