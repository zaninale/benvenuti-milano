# Benvenuti a Milano

> Claude Impact Lab Milano · 3 October 2026 · Track 01 · Welcome journey for people arriving in Milan

**One line:** people who have just arrived in Milan describe themselves in their own language, by
text or voice, and get a personal, dated plan of what to do, in which order and where, with the
City's sources; at the counter, staff open the same plan from a QR code and approve answers that
Claude drafts with sources.

**Demo video:** <link>

## The problem

Ana arrived yesterday from Brazil to study at the Politecnico (an invented case). In her first eight
working days she must apply for a residence permit, then register her residence within 20 days,
enrol in the health service, file the waste tax within 90 days. The rules are spread across the
Police HQ, Poste, the Comune, the Revenue Agency and the Region, mostly in Italian, sometimes
contradicting each other. Nobody tells her the order, and nobody tells her which deadline comes
first. She also struggles to read small text.

## What we built

One web page with two sides: the citizen and the registry counter.

**Two ways in:** write or dictate in any language, or fill in the forms (who is moving, citizenship,
reason, arrival, nearest metro stop or university, tools and documents already held); both produce
the same profile card to confirm, and while Claude works the page shows its real steps.

1. **Ana tells her story** in Portuguese, typed or dictated: *"Sou brasileira, cheguei ontem para um
   mestrado no Politecnico, moro perto da estação Piola…"*. No names, no documents, no address.
2. **Claude understands and asks only what is missing**, one question at a time, then shows a
   **profile card**: who is moving, citizenship area, reason, arrival date, the metro stop, the
   tools she already has (email, phone, Italian SIM, device, SPID/CIE).
3. **Ana confirms the card.** Only then Claude reads the City's catalogue, finds the nearest registry
   office in the City's open data and submits a plan. The server checks the plan, computes the
   dates and attaches links and sources.
4. **Ana gets her plan in Portuguese**, eight steps in dependency order: residence permit (by
   14 Oct), tax code (16 Oct), residence (22 Oct), health enrolment, home check (until 6 Dec),
   Italian SIM (recommended, after the tax code), digital identity (after residence), waste tax
   (by 31 Dec). Each step shows priority, office, channel, **verification status** (official,
   secondary, to be verified, conflicting sources), instructions in her language, official links
   ("to be confirmed" when not verified), sources with retrieval date, and a **QR code** that holds
   only the journey code and the step number. The nearest registry office (Municipio 3, 0.6 km from
   Piola) and the points where sources disagree are shown beside the plan.
5. **Accessible by design:** dictation, a **Listen** button that reads the answer or the whole plan
   aloud in her language, large text, high contrast, and an **.ics calendar** with every deadline
   and a reminder two days before (proactive, without personal data).
6. **Questions about the plan** in any language: Claude answers from her plan and the catalogue,
   says where the information comes from and flags conflicts.
7. **At the counter** (tab *Sportello*), Giulia types the code or scans a step QR (`MI-XXXX-4` opens
   step 4), sees the profile in Italian with automatic warnings, and asks Claude. Claude drafts an
   answer with sources, conflicts in evidence and a translation for Ana. Giulia corrects or
   approves it; only then does the answer appear in Ana's plan.

The second invented case, Vikram (engineer from India, with his wife and 6-year-old daughter),
also runs end to end: one plan for the family, steps marked per person, one residence declaration
signed by the adults.

The catalogue covers **14 profiles**: Italians moving from another town, returning from abroad
(AIRE) or studying away from home; EU citizens for short stays, work, study or with their own
resources; non-EU citizens for short visits, study, employment, self-employment, family
reunification, or with a permit from another EU country; and special situations (family members of
Italian or EU citizens, international protection, other cases), which get a single step that
refers the person to the competent office.

## Where Claude works

*What Claude does every time someone uses this.*

- **Model:** `claude-sonnet-5-5` through the Anthropic API (`CLAUDE_MODEL`), adaptive thinking,
  effort `low` for the conversation and `medium` to build the plan (`AGENT_EFFORT`,
  `AGENT_PLAN_EFFORT`). At most 6 tool rounds per request; `max_tokens` 4,000 (chat, counter) and
  12,000 (plan).
- **What it does at runtime:**
  - understands the person in any language, typed or dictated, and replies in that language in
    plain words;
  - works out who is moving and each person's situation, never inferring citizenship from a name
    or a language, and asks one question at a time for what is missing;
  - picks one of the catalogue's 14 profiles for each adult, using the criteria in the catalogue
    (the list and the criteria are read from `data/procedures.yaml` into the system prompt and the
    `propose_profile` schema);
  - maps the person to the catalogue profiles and reasons over the catalogue's rules: which
    procedures apply, which variant (e.g. the student variant of the waste tax), which enabling
    tools are needed only because the person lacks them, and in which order;
  - writes every step's title and instructions in the person's language, without adding facts;
  - picks the nearest registry office from the City's open data;
  - answers follow-up questions from the plan and the catalogue, citing the source;
  - at the counter, drafts a sourced answer in Italian plus a translation, and flags conflicts.
- **Prompts and tools:** system prompts in [`prompts/agent_citizen.md`](prompts/agent_citizen.md)
  and [`prompts/agent_counter.md`](prompts/agent_counter.md), loaded by [`agent.py`](agent.py).
  Tools in [`tools.py`](tools.py), all deterministic, with strict JSON schemas:
  - `get_catalog(profile_ids)`: applicable procedures from `data/procedures.yaml`, with the
    household rules, tool rules, conflicting points and variants (no URLs: the server adds them);
  - `compute_deadline(arrival_date, procedure_id)`: dates computed by code;
  - `find_offices(near)`: nearest registry offices from a metro stop, a university site or
    coordinates;
  - `propose_profile(...)`: the profile card the citizen must confirm;
  - `submit_plan(steps)`: the plan, checked and completed by the server;
  - `draft_answer(...)` (counter): the draft the officer approves.
- **What it decides, and what a human confirms:**
  - Claude proposes the profile: the citizen confirms the card before any plan is built; the server
    refuses a plan without that confirmation.
  - Claude builds the plan: the citizen reads it, ticks steps as done, and checks the flagged
    points at the desk.
  - Claude drafts the counter answer: the officer approves or corrects it before the citizen sees it.
- **What happens when it's wrong:**
  - The server rejects unknown procedure ids and orders that break `dipende_da`, and sends the
    error back to Claude, which fixes and resubmits. It also refuses a plan built before Claude has
    read the catalogue.
  - Steps that do not seem to apply to the confirmed profile, or that apply only under a condition
    (e.g. "if the lease is in your name"), are accepted but logged as warnings shown at the counter.
  - Dates are computed by code (working days skip weekends, national holidays and Sant'Ambrogio).
    Links and sources come from the catalogue: Claude never writes a date or a URL into the plan.
  - Every step shows its verification status; conflicting sources are listed beside the plan.
  - API errors, rate limits or refusals show a clear message, and the conversation goes back to
    where it was before the request.
- **Switch the AI off:** what's left is a YAML catalogue and three datasets. No profile, no plan,
  no answers.

## City data and sources

| Source | How we used it |
|---|---|
| `ds549-sedi-dei-servizi-anagrafici` (13 offices; dataset updated 8 May 2026, retrieved 3 Oct 2026) | Nearest registry office as the crow flies; opening hours and booking notes |
| `ds535_atm-fermate-linee-metropolitane` (130 stops; updated 24 Jul 2026, retrieved 3 Oct 2026) | "I live near Piola": a location without an address |
| `ds94-infogeo-atenei-sedi-localizzazione` (90 sites; updated 8 May 2026, marked as never updated, retrieved 3 Oct 2026) | Students: "near the Politecnico" |
| comune.milano.it: TARI occupancy declaration; residence request for foreign nationals from abroad; change of residence; electronic ID card. Retrieved 3 Oct 2026 | Waste tax, residence and digital identity steps |
| yesmilano.it: Study & Work guide to the residence permit; residence for students and health service step by step (these two links still to be confirmed). Retrieved 3 Oct 2026 | Immigration Desk, student residence, home check, health enrolment |
| ANPR, Polizia di Stato, Portale Immigrazione, Poste Italiane (residence permit, PosteID), Agenzia delle Entrate, Portale Integrazione Migranti, Regione Lombardia, ATS Milano, Your Europe. Retrieved 3 Oct 2026 | Procedures, documents, fees and verification status, listed per step in [`data/procedures.yaml`](data/procedures.yaml) |
| Secondary sources (university pages, third-party guides) | Shown as "secondary" or "conflicting sources", never as official |
| A colleague's working document "Arrivare a Milano" (profiles, procedures and offices in YAML), verified 3 Oct 2026 | 14 profiles with their selection criteria and 17 procedures, imported with their sources, verification date and status by [`scripts/import_catalogo.py`](scripts/import_catalogo.py) |
| esteri.it and "Il visto per l'Italia", Ministero dell'Interno, Ministero della Salute, European Commission, Your Europe, Prefettura and Questura di Milano (retrieved by the colleague, 3 Oct 2026, where a date is given) | Visa, clearances, EU residence rights, health cover, citizenship, special situations |

Links, documents and fees for residence permits, residence and the electronic ID card were checked
on 3 Oct 2026 against a second catalogue that a colleague verified on the official pages that day.

Open data are © Comune di Milano, Creative Commons Attribution, through the CKAN API
([`opendata.py`](opendata.py)). They are cached in `data/cache/`, with a reduced copy in
[`data/opendata/`](data/opendata/) so the demo also works offline.

## Day one

- **Build on what the City already does:** the welcome emails for new residents can carry the link
  to the plan; the YesMilano student path is already linked in the steps.
- **To switch it on:** a City editor who owns `data/procedures.yaml` (41 procedures, 14 profiles,
  3 open conflicts, 3 links to confirm) and the counter staff's flags; an Anthropic API key; HTTPS
  hosting; authenticated access for counter staff (open in this prototype).
- **The plan comes out as a PDF,** generated on request from the journey code: the person keeps it
  or sends it by email from their own device, and the City stores no personal data.
- **What a proactive version 2 needs:** a consented signal that someone has just arrived (for
  example the residence application), and an email or phone number the person chooses to give, for
  reminders before each deadline. Today the .ics file does it without any personal data.
- **Version 2 would add:** households of housemates and mixed origins (separate declarations),
  contextual tips that reuse planned visits ("while you are at the post office…"), the interface
  in more languages (the plan is already in the person's language), officer flags back to the
  catalogue editors, plans that survive a server restart.
- **The catalogue includes content imported from a colleague's working document**, with its
  sources: the profiles for Italians returning from abroad (AIRE), Italian students from another
  town, self-employed workers and special situations; the steps before leaving (visa, work and
  family clearances); renewals and citizenship; the EU registration certificate; the presence
  declaration for short stays. Our entries take precedence: where a procedure was already ours, only
  the new sources were added (the Police HQ appointment and the permit collection stay inside our
  permit steps). Imported entries keep the colleague's verification date and status: the 9 marked
  "to be verified" stay so. Deadlines, dependencies and channels were taken only from explicit
  sentences; otherwise no deadline, channel "to be verified", priority "important". Steps "before
  leaving" enter a plan only if the person has not arrived yet; renewals and citizenship are used to
  answer questions. The import is a script over the data ([`scripts/import_catalogo.py`](scripts/import_catalogo.py)),
  not new code.
- **Version 2 would also add:** dedicated procedures for family members of Italian or EU citizens
  and for international protection (today a single step refers to the competent office);
  deadlines that start from a permit renewal; checking the 9 imported entries still "to be
  verified".
- **Open points to verify with the City:**
  - who carries out the home check;
  - the health-service fee for international students;
  - SPID for foreign nationals with only a residence permit;
  - for EU citizens, whether registering within 90 days is a legal deadline: Your Europe says you
    register after three months (`RES_U`);
  - for salaried non-EU workers, whether the 8 working days apply to the Immigration Desk
    appointment, with the postal kit filed after the residence contract (`PERM_L`);
  - the YesMilano pages for students' residence and health enrolment, which may have moved.

## Privacy

- No names, documents, addresses, emails or phone numbers are asked for or stored. People in a
  household are "You", "Person 2".
- A journey is identified by a random code (`MI-XXXX`); QR codes hold only the code and the step.
- Conversations and plans live only in server memory and expire (2 hours and 7 days). Nothing is
  written to disk. Logs record only tool names, catalogue profiles and the metro stop.

## Run it

Windows PowerShell, Python 3.12+:

```powershell
git clone <this repo>
cd <repo>
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # add your ANTHROPIC_API_KEY
python app.py            # open http://localhost:5000
```

Tests (one per profile), and the live tests on Ana's case and on three imported profiles (they call
Claude):

```powershell
python -m pytest -q
$env:RUN_LIVE=1; python -m pytest -q tests/test_live_ana.py tests/test_live_profili.py -s
```

`python opendata.py` downloads the three datasets again.

| File | What it does |
|---|---|
| `app.py` | Flask endpoints: `/api/chat`, `/api/confirm`, `/api/plan/<code>`, `/api/plan/<code>.ics`, `/qr/<code>/<n>.svg`, `/api/counter/ask`, `/api/counter/approve` |
| `agent.py` | Claude tool-use loop for the citizen and the counter |
| `tools.py` | Deterministic tools, date rules, checks on the plan |
| `catalog.py` | Loads and validates `data/procedures.yaml` (procedures and profiles) at start-up |
| `scripts/import_catalogo.py` | Converts the colleague's YAML content into our schema and merges it |
| `opendata.py` | City open data via CKAN, cache and offline copy |
| `store.py` | In-memory state with expiry |
| `templates/`, `static/` | The single page, from the validated mockup in `docs/mockup.html` |

## Team

| Name | Role | GitHub |
|---|---|---|
| | | |

## Licence

MIT. Built at the Claude Impact Lab Milano and donated to the Comune di Milano.
