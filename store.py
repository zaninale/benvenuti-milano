"""Stato solo in memoria, con scadenza: niente database, le conversazioni non vanno su disco."""
import secrets
import time

SESSION_TTL = 2 * 3600       # una conversazione dura al massimo 2 ore
PLAN_TTL = 7 * 24 * 3600     # un codice percorso vale 7 giorni (finché il server è acceso)
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # senza 0/O e 1/I, facili da confondere allo sportello

SESSIONS: dict[str, dict] = {}
PLANS: dict[str, dict] = {}


def _purge() -> None:
    now = time.time()
    for d, ttl in ((SESSIONS, SESSION_TTL), (PLANS, PLAN_TTL)):
        for k in [k for k, v in d.items() if now - v["_t"] > ttl]:
            del d[k]


def get_session(sid: str | None) -> tuple[str, dict]:
    """Restituisce la sessione, o ne crea una nuova con un id casuale."""
    _purge()
    if sid and sid in SESSIONS:
        SESSIONS[sid]["_t"] = time.time()
        return sid, SESSIONS[sid]
    sid = secrets.token_urlsafe(16)
    SESSIONS[sid] = {"_t": time.time(), "messages": [], "pending": [], "card": None, "confirmed": False,
                     "plan_code": None}
    return sid, SESSIONS[sid]


def new_code() -> str:
    while True:
        code = "MI-" + "".join(secrets.choice(ALFABETO) for _ in range(4))
        if code not in PLANS:
            return code


def save_plan(plan: dict) -> None:
    _purge()
    plan["_t"] = time.time()
    PLANS[plan["code"]] = plan


def get_plan(code: str) -> dict | None:
    _purge()
    return PLANS.get((code or "").strip().upper())
