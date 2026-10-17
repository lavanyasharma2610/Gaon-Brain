# ARCHITECTURE.md

Two doors on one backend:
- Awaaz Mode: voice-first screen, big mic, 4 core actions.
- Poora App: full dashboard.

Backend: FastAPI + SQLModel/SQLite (data/gaon.db), event-sourced core. All user actions are events; derived state recomputed by projections.

Frontend: React+TS+Vite+Tailwind (planned); current scaffold uses plain HTML pages wired to backend.

Modules: app/voice, glut, sim, sanjha, radar, bazaar, productivity, shock, suraksha, providers, models, events, projections, seed, config.

Providers: PriceProvider (csv|datagov), WeatherProvider (sample|openmeteo), DiseaseProvider (demo|http), OcrProvider (none|tesseract). Chosen by env flags in .env.
EOF