# Benvenuti a Milano

> Claude Impact Lab Milano · 3 October 2026 · Track 01

**One line:** people who have just arrived in Milan describe themselves in their own language, by
text or voice, and get a personal, dated plan of what to do, in which order and where, with the
City's sources; at the counter, staff open the same plan from a QR code.

**Demo video:** <link>

## The problem

Ana arrived yesterday from Brazil to study at the Politecnico. In her first eight working days she
must apply for a residence permit, then register her residence within 20 days, enrol in the health
service, file the waste tax within 90 days. The rules are spread across the Prefecture, the Police
HQ, Poste, the Comune, the Revenue Agency and the Region, mostly in Italian, sometimes contradicting
each other. Nobody tells her the order, and nobody tells her which deadline comes first.

## What we built

<step by step, with one or two screenshots>

## Where Claude works

*What Claude does every time someone uses this.*

- **Model:** `claude-sonnet-5-5` through the Anthropic API.
- **What it does at runtime:**
  - understands the person in any language, by text or dictated voice;
  - works out who is moving (one person, a family, housemates) and each person's situation, and
    asks one question at a time for what is missing;
  - reasons over the City's rules in `data/procedures.yaml`: which procedures apply, in which
    order, which ones depend on others, and which tools the person still needs (email, phone,
    digital identity);
  - writes the instructions in the person's language;
  - picks the nearest registry office from City open data;
  - at the counter, drafts a sourced answer for the officer and flags conflicting sources.
- **Prompts and tools:** `prompts/agent_citizen.md`, `prompts/agent_counter.md`; tools in
  `tools.py`: `get_catalog`, `compute_deadline`, `find_offices`, `propose_profile`, `submit_plan`.
- **What it decides, and what a human confirms:**
  - Claude proposes the profile: the citizen confirms it before any plan is built.
  - Claude builds the plan: the citizen ticks the steps.
  - Claude drafts the answer at the counter: the officer approves or corrects it before the
    citizen sees it.
- **What happens when it's wrong:**
  - Claude can only cite procedures that exist in the catalogue, and the server rejects unknown
    ones.
  - Dates are computed by code, not by the model.
  - Links and sources are attached by the server from the catalogue.
  - Every step shows its verification status: official source, secondary source, to be
    verified, or conflicting sources.

## City data and sources

| Source | How we used it |
|---|---|
| `ds549-sedi-dei-servizi-anagrafici` | Nearest registry office |
| `ds535_atm-fermate-linee-metropolitane` | "I live near…" without an address |
| `ds94-infogeo-atenei-sedi-localizzazione` | Students: offices near their university |
| comune.milano.it: TARI occupancy declaration, residence for foreign nationals (retrieved 3 Oct 2026) | Procedures, channels, deadlines |
| ANPR, Poste Italiane, Regione Lombardia, Agenzia delle Entrate, Your Europe, YesMilano (retrieved 3 Oct 2026) | Procedures and verification status, listed per step in `data/procedures.yaml` |

## Day one

- **Build on what the City already does.** The plan can start from the welcome emails the City
  already sends to new residents, and link the YesMilano student path.
- **What a proactive version 2 needs:**
  - a consented signal that someone has just arrived, for example the residence application;
  - the email the person chooses to give, for reminders before each deadline;
  - a City editor who reviews the catalogue and the counter staff's flags.
- **Open points to verify with the City:**
  - who carries out the home check;
  - the health-service fee for international students;
  - SPID for foreign nationals.

## Run it

```powershell
git clone <this repo>
cd <repo>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # add your ANTHROPIC_API_KEY
python app.py            # open http://localhost:5000
```

## Team

| Name | Role | GitHub |
|---|---|---|
| | | |

## Licence

MIT. Built at the Claude Impact Lab Milano and donated to the Comune di Milano.
