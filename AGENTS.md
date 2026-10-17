# AGENTS.md

Project: Gaon Brain (गाँव ब्रेन). See docs/SPEC.md for full spec.

## Stack
- Backend: Python 3.11+, FastAPI, SQLModel/SQLAlchemy, SQLite under data/.
- Frontend: React + TypeScript (strict) + Vite + Tailwind. No Next.js.
- Everything runs locally, no cloud, no paid keys.

## Commands
- make setup | seed | dev | test | lint | reset-demo
- scripts/dev.py cross-platform launcher (backend + frontend together).

## Checkpoint Protocol
- One phase at a time. After phase (tests green, committed, tagged): STOP.
- Post checkpoint message (built bullets, run commands + URL, 5-step click-through, simulated/assumed, known issues, screenshots from P2).
- Ask user "Does it behave as expected? ... Reply 'go' to continue".
- Wait. Apply changes as small commits. Record feedback in docs/FEEDBACK.md. Then update docs/PROGRESS.md, tag phase.
- Never combine phases. If no reply, do not continue.
- At start of new session: read AGENTS.md, docs/PROGRESS.md, relevant spec sections.

## Honesty rules
- No real-world statistics; all data synthetic, labelled in UI/docs.
- Fictional village, no real person's data.
- No dead buttons, no "coming soon", no lorem ipsum.
- Never claim accuracy for disease detection/forecasts/fraud. Show confidence + "expert se poochho" when low.
- App never submits to government/insurer; never queries PMFBY.
- Every simulated number labelled; assumptions visible (info popover).

## Git
- Small logical commits, tests passing. Conventional Commits. Tag after approved phase: v0.1..v0.10, final v1.0.0.
- No remote; never push; never rewrite history.
- .gitignore: venv, node_modules, dist, data/*.db, data/uploads, .env, __pycache__, .DS_Store. Commit .env.example.
