# Preparare la cartella (PowerShell, 5 minuti)

```powershell
# 1. Estrai questo kit in C:\Dev\CLAUDE_IMPACT_LAB
cd C:\Dev\CLAUDE_IMPACT_LAB

# 2. Clona il repo del Lab come contesto (escluso dal tuo repo dal .gitignore)
git clone https://github.com/Claude-Milano/impact-lab-oct-2026 _hub

# 3. Inizializza il repo del team: il primo commit deve essere di oggi, dopo le 10:00
git init
git add .
git commit -m "Kit iniziale: catalogo, mockup, personas, CLAUDE.md"

# 4. Chiave API: crea .env dal modello e inserisci la tua ANTHROPIC_API_KEY
copy .env.example .env

# 5. Apri Claude Code nella cartella e incolla il prompt di PROMPT_CLAUDE_CODE.md
claude
```

Per pubblicare: crea un repo pubblico su GitHub, poi
`git remote add origin https://github.com/<utente>/<repo>.git` e `git push -u origin main`.
Controlla prima che `.env` non sia nel commit (`git status` non deve mostrarlo).
