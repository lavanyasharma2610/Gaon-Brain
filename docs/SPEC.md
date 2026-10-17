# GAON BRAIN (गाँव ब्रेन): BUILD SPEC

You are a senior full-stack engineer. Build this hackathon project end to end on
this laptop. When something is ambiguous, pick the simplest reasonable option,
record it in docs/DECISIONS.md, and continue within the current phase.

## 1. CHECKPOINT PROTOCOL (mandatory, overrides any "work autonomously" idea)
Work ONE phase at a time. After a phase is finished (tests green, committed,
tagged):
1. STOP. Do not start the next phase.
2. Post a checkpoint message containing:
   a. What was built (5-8 bullets).
   b. Exact commands to run and the URL/page to open.
   c. A 5-step click-through the user can follow to try it.
   d. What is simulated or assumed.
   e. Known issues or shortcuts.
   f. Screenshots at docs/screenshots/phase-N/ (from P2 onward).
3. Ask the user: "Does it behave as expected? What should change in behaviour,
   Hindi wording, layout or colours? Anything to add, remove or reorder? Any
   number or assumption to change? Reply 'go' to continue, or list changes."
4. Wait for the reply. Apply requested changes as small commits (fix:/refactor:),
   re-run tests, post a short summary of what changed, and ask again. Repeat
   until the user says "go".
5. Record the user's feedback and your decisions in docs/FEEDBACK.md. Only then
   update docs/PROGRESS.md, tag the phase, and start the next one.
Never combine two phases without approval. If the user has not replied, do not
continue. At the start of any new session, read AGENTS.md, docs/PROGRESS.md and
the relevant sections of this spec before doing anything.

## 2. PRODUCT
Gaon Brain is a voice-first, village-level coordination system for farmers.
Problem: each farmer decides alone (often from last season's price), so a village
over-plants the same crop and prices fall; tractors clash on the same days; farm
power arrives at unpredictable hours; animal raids and crop disease are invisible
across plots; sales, payments, purchases and crop losses are not recorded.
Core idea: one shared village ledger ("Gaon Khata") plus a "Brain" that plans
across ALL plots and explains every suggestion ("Kyun?"), without making any
farmer worse off than their own baseline (inside the model only).
Hero line: "Ek Awaaz, Poora Gaon."

Pillars (loop: Plan > Grow > Harvest > Sell > Learn):
1. Ek Awaaz: voice/tap events, Bol-Bechi Khata, Bhav Tulna.
2. Gaon Plan: Glut Guard, price series, productivity benchmark.
3. Gaon Sanjha: tractor schedule, irrigation slots, bijli window, Sinchai Card.
4. Gaon Radar: disease reports (Fasal Doctor) and animal sightings on one map.
5. Gaon Bazaar: staggered-harvest bulk lots, buyer commitments, payments, buyer
   trust score.
6. Khata Suraksha (personal protection layer): Claim Kit, Kharid Check, Season
   Report, Village Mitra mode.

Two doors on one backend:
- Awaaz Mode: voice-first screen, huge mic button, no reading required, spoken
  confirmations, only the 4 core actions (sale, power on/off, animal sighting,
  disease/loss report).
- Poora App: the full dashboard. A toggle switches modes and is remembered.

Signature demo: ONE event (e.g. "blight reported on 3 plots") propagates through
the pillars: Radar alerts nearby plots > expected yield drops > Bazaar lot
quantity changes > Glut Guard re-plans harvest weeks > water slots rebalance >
every affected farmer gets a one-line "Kyun?" explanation.

## 3. HARD CONSTRAINTS
- Everything runs locally. No cloud services, no paid keys required. Optional
  providers (mandi price, weather, vision, OCR) sit behind env flags with offline
  fallbacks, so the demo works with zero internet and zero keys.
- Backend: Python 3.11+, FastAPI, SQLModel/SQLAlchemy, SQLite file under data/.
- Frontend: React + TypeScript (strict) + Vite + Tailwind. No Next.js.
- One-command setup and run on Windows/macOS/Linux: Makefile AND a cross-platform
  launcher scripts/dev.py that starts backend and frontend together.
- Do NOT invent real-world statistics. All data is synthetic and labelled as such
  in the UI and docs. Fictional village, no real person's data.
- No dead buttons, no "coming soon", no lorem ipsum. Unbuilt things appear only
  as roadmap in docs.
- Never claim accuracy for disease detection, forecasts or fraud detection.
  Show confidence and an "expert se poochho" path when confidence is low.
- The app never submits anything to any government or insurer system. It does not
  query PMFBY or any official portal.

## 4. DATA MODEL (event-sourced core)
Tables: villages, farmers, plots (area_acre, polygon, crop, sown_on, health,
expected_yield, feeder_id), events (id, type, plot_id, farmer_id, mitra_id, lat,
lon, ts, payload JSON, raw_text), sales, buyers, lots, commitments,
tractor_requests, power_logs, water_slots, plans, plan_items, reports, claims,
claim_photos, purchases, consents, mitra_audit, uploads.
All user actions are events. Derived state (plot health, expected yield, lots,
schedules, trust scores) is recomputed from events by projection functions.
`python -m app.seed` creates a fictional village: ~24 farmers, ~30 plots
(generated grid polygons), 2 seasons of history, 3 tractors, 2 feeders, 6 buyers,
sample purchases and a synthetic mandi price/arrivals CSV (header comment:
SYNTHETIC DATA).

## 5. BACKEND MODULES (each: service code, router, pydantic schemas, tests)

5.1 Voice parser (app/voice)
Rule-based (regex + dictionaries), no LLM required. Handle Hindi, Hinglish and
Devanagari digits and number words ("paanch sau", "dedh sau", "sadhe teen").
Units configurable (kilo/kg, quintal, maund with a conversion table in config).
Intents: record_sale, power_on, power_off, animal_sighting, disease_report,
tractor_request, sowing_plan, irrigation_done, loss_report. Fuzzy-match crop and
buyer names (rapidfuzz). Totals computed in code (qty_kg x rate), never guessed.
Confirm loop as a state machine per session: parsed > confirm card > haan/nahi >
save or re-ask; ask for one missing field at a time. Confirm words (haan/nahi)
handled by keyword rules, not by any model.
Endpoints: POST /voice/parse, POST /voice/confirm. Tests: >= 30 sentences.

5.2 Glut Guard (app/glut)
Inputs: plots with area, crop parameter table (base price P0, yield/acre,
cost/acre, weekly demand D, feasible weeks), price sensitivity K, scenarios.
- supply S(c,w) = sum(area x yield) of plots assigned (c,w)
- price(c,w) = clip(P0 x (1 - K x (S/D - 1)), 0.3*P0, 1.8*P0)
- profit(plot,c,w,scenario) = area x (yield x yield_mult x price x price_mult - cost)
- Greedy sequential assignment in a deterministic seeded order; each plot picks
  the feasible (crop, week) maximising profit given supply already assigned.
- Baseline = each plot's own original choice priced under the same model.
- Floor check: if a plot's planned profit < its baseline in the normal OR bad
  scenario, it keeps the baseline. Iterate until no violations (cap iterations,
  report convergence).
- Rotation: plots moved last season are moved last this season.
- Output: plan, per-plot one-line explanation (Hindi + English templates: why
  this crop/week, expected profit vs baseline), village profit before/after, max
  crop share before/after, farmers_worse_off (must be 0).
Endpoints: GET /glut/state, POST /glut/plan, POST /glut/apply.
Tests: property test over many random seeds asserting farmers_worse_off == 0 and
that max crop share does not increase.

5.3 Simulation (app/sim)
- Multi-season cobweb: next-season crop shares respond to last season's profit
  with a lag ("before").
- Adoption sweep alpha in {0, 30, 60, 100}%: alpha of farmers follow the plan,
  the rest follow the naive rule.
- Shock simulation: price or yield shock, then re-run.
- Backtest: replay the synthetic CSV, report MAE of predicted vs actual price.
All parameters in config, labelled "illustrative, not calibrated".
Endpoints: POST /sim/cobweb, POST /sim/adoption, POST /sim/shock.

5.4 Gaon Sanjha (app/sanjha)
- Tractor scheduler: requests (want_date, prev_served_count), per-tractor daily
  hour capacity, fair order (fewest prior services first, then earliest
  deadline), clash goes to the next day. Report peak daily demand with and
  without Glut Guard staggered sowing dates.
- Bijli window: from power_logs per feeder, hourly P(on) = on_days/total_days,
  best contiguous 3-hour window; require a minimum number of days of data.
- Irrigation slots: assign plots to slots inside the bijli window under a village
  pump-hours budget; plot need from a crop interval table (PLACEHOLDER values,
  flagged in docs/ASSUMPTIONS.md), days since sowing and plot health.
Endpoints: GET/POST /tractor/*, GET /power/window, GET/POST /water/slots.

5.5 Gaon Radar and Fasal Doctor (app/radar)
Disease reports and animal sightings with lat/lon and ts. Haversine distance.
Alert rule: >= N same-type reports within R km in D days (defaults 3 / 2 km /
5 days, in config, flagged as assumptions). Heatmap on a grid with recency
weighting.
Fasal Doctor: photo upload (stored under data/uploads with SHA-256) goes to a
DiseaseProvider interface: `demo` provider (user picks condition and confidence,
deterministic) and an optional `http` provider from env. Result: condition,
confidence, remedies sorted CHEAPEST FIRST using a small curated sample table
labelled "sample data, not agronomic advice". If confidence < 0.7 show
"expert se poochho". A diagnosis creates a disease_report event, so it appears
on the Radar map. Disease-to-yield loss factor is config (default 20%, flagged
assumption).
Endpoints: POST /radar/report, POST /doctor/analyze, GET /radar/alerts,
GET /radar/heatmap.

5.6 Gaon Bazaar (app/bazaar)
Bulk lots built from the staggered harvest plan (crop, week, expected_qty).
Seeded fictional buyers can commit to lots (mock). Payment records tied to sales
with due dates and overdue flags. Buyer trust score = (on_time + 1) / (n + 2),
on_time meaning paid within due date + 5 days; show n and a "sample data" label;
hide the score when n < 3.
Endpoints: GET /bazaar/lots, POST /bazaar/commit, GET /bazaar/payments,
GET /bazaar/buyers.

5.7 Productivity and Season Report (app/productivity)
Anonymous benchmark: group plots by crop and sowing-date bucket, compare yield per
acre; hide any group with fewer than 5 plots. Per-farmer Season Report: yield per
acre, cost, revenue, profit versus the anonymous benchmark.
Endpoints: GET /productivity/benchmark, GET /report/season/{farmer_id}.

5.8 Shock chain (app/shock)
POST /shock {type: disease|rain|price_drop, plot_ids?, magnitude} writes events
and returns an ordered list of effects (Radar > Yield > Bazaar > Glut re-plan >
Sanjha rebalance) plus per-farmer "Kyun?" lines, using the services above.
Target < 1 s on seed data. This is the demo centrepiece.

5.9 Khata Suraksha (app/suraksha)
a) Bhav Tulna: on every sale, show the nearest market's modal price from
   PriceProvider next to the sold rate, with the difference and the data date.
   If data is missing or older than 7 days, say so plainly.
b) Sinchai Card (per plot): skip if forecast rain_mm_48h >= 10 and probability
   >= 60; irrigate if days_since_last_irrigation >= crop interval (placeholder,
   adjusted by plot health); otherwise wait. Show the probability, not
   certainty, with a one-line reason in Hindi. days_since comes from irrigation
   events. Weather via WeatherProvider (sample | openmeteo).
c) Claim Kit: start a claim (event type, event_at); show a 72-hour countdown
   from event_at; store policy_no, survey_no, crop, insured_area and a
   SELF-REPORTED policy status (active/inactive/unknown) with the note "verify
   on the official PMFBY portal; this app does not query it". Photos: browser
   geolocation lat/lon, server timestamp, SHA-256, weather snapshot for that
   day. Generate a PDF dossier (ReportLab; bundle an OFL-licensed Noto Sans
   Devanagari TTF under backend/assets/fonts and TEST that Hindi renders):
   farmer, policy fields, sowing record, photos with GPS and time, weather,
   related purchases. Final screen: "Official reporting: Crop Insurance App or
   helpline 14447 (verify current channels)". Never imply the insurer accepts the
   PDF; docs/LIMITATIONS.md must say it does not help widespread yield-loss
   claims decided by crop-cutting results, and that the integrity hash is a
   signal, not legal proof.
d) Kharid Check: manual inputs (product, printed MRP, price paid, bill received
   yes/no, dealer name, optional photo). Compute overcharge = paid - MRP, flag a
   missing bill, generate a complaint draft (Hindi and English) containing only
   the entered facts, and flag a dealer pattern when >= 3 village reports name
   the same dealer (config). OCR is optional behind a flag. State clearly in UI
   and docs that it CANNOT detect fake products.
e) Village Mitra mode: role "mitra". The farmer generates a 4-digit consent code
   valid 24 hours; the mitra may add events for that farmer only with a valid
   code; events carry mitra_id; every action is written to mitra_audit; a
   commission counter per confirmed entry (config rate, labelled hypothetical).
Endpoints under /suraksha/*.

5.10 Providers (app/providers)
PriceProvider (csv | datagov), WeatherProvider (sample | openmeteo), DiseaseProvider
(demo | http), OcrProvider (none | tesseract). Cached, offline fallbacks, chosen
by env, documented in .env.example.

5.11 Cross-cutting
pydantic-settings config, structured logging, CORS for localhost, OpenAPI at
/docs, consistent error format, ruff and mypy clean.

## 6. FRONTEND (mobile-first, Hindi default, English toggle)
Pages: Gaon ki Sthiti (overview + alerts), Ek Awaaz (voice + logbook ledger),
Gaon Plan (village map, crop share, plan vs baseline, Kyun? drawer, adoption
slider, before/after cobweb chart), Gaon Sanjha (tractor calendar, water slots,
bijli window chart, Sinchai Card), Gaon Radar (map, report form, Fasal Doctor,
alerts), Gaon Bazaar (lots, commitments, payments, buyer trust), Khata Suraksha
(Claim Kit, Kharid Check, Season Report, Mitra console), Jhatka panel (shock
buttons + animated chain where each pillar visibly updates).
Voice UI: Web Speech API (hi-IN) with typed fallback, big mic button, live
transcript, confirm card with Haan/Nahi, spoken replies via speechSynthesis.
Village map: inline SVG from plot polygons (no tile server, works offline),
styled like a revenue/khasra field map.
Persistent badges "नमूना डेटा / Sample data" and "सिमुलेशन" on every simulated
panel. Assumptions visible in an info popover, never hidden.
Accessibility: body text >= 18px on mobile, touch targets >= 48px, WCAG AA
contrast, keyboard navigable, honour prefers-reduced-motion.

## 7. DESIGN BRIEF (must NOT look AI-generated)
Concept: a modern take on the Indian bahi-khata (ledger) and patwari field map.
- Palette (starting point, tune by eye): paper #F4EFE3, ink #1E1B16, field green
  #3F5E3A, turmeric #C98A12, terracotta #B4492D, indigo-dye #2F3E6B, river-grey
  #8A9096. Define as CSS variables / Tailwind tokens. Flat colours.
- Type: self-host fonts via @fontsource (verify package names): Noto Sans
  Devanagari for UI, a Devanagari serif (e.g. Tiro Devanagari Hindi or Martel)
  for headings, a clean Latin pairing (e.g. IBM Plex Sans). Strong hierarchy,
  tabular figures for numbers.
- The Ek Awaaz page looks like a ruled ledger (ruled lines, column headers,
  ink-style entries), not generic cards. The map uses hatching and outlines like
  a cadastral map.
- Layout: not a stock SaaS dashboard. Mobile: bottom nav. Desktop: asymmetric,
  map as the main object, content in a ledger-style side column.
- Custom SVG icons in one consistent stroke style. No emoji as icons.
- FORBIDDEN: purple/blue gradients, gradient text, glassmorphism/blur cards,
  glowing shadows, floating blobs, rounded-2xl on everything, centered hero with
  "Welcome to ...", stock-illustration people, "AI sparkle" motifs, identical
  card grids of icon + title + description.
- Copy: short, specific, written like someone who knows villages. Real Hindi
  (not transliterated) for primary text. No marketing filler.
- Motion: purposeful only (shock chain, map recolour on re-plan), 150-250 ms.
- Charts fully restyled to the tokens, direct labels instead of legends.

## 8. TESTING AND VERIFICATION
- pytest for every backend module; property tests for Glut Guard.
- Vitest for frontend utilities; Playwright smoke test through the demo.
- After each phase: run tests, run the app, exercise endpoints with curl.
- Before each checkpoint (from P2): Playwright screenshots of changed pages at
  390px and 1280px, review against section 7, fix, re-shoot, save to
  docs/screenshots/phase-N/.
- Never mark a phase complete if tests fail or a page is broken.

## 9. GIT WORKFLOW
- Small logical commits, tests passing before each. Conventional Commits.
- Tag after each approved phase: v0.1 ... v0.10. Final tag v1.0.0.
- .gitignore: venv, node_modules, dist, data/*.db, data/uploads, .env,
  __pycache__, .DS_Store. Commit .env.example, never secrets.
- No remote is configured; never push; never rewrite history.

## 10. DOCS (kept current)
README.md (what it is, 5-minute setup, run, demo path, architecture sketch,
screenshots, honest limitations), docs/ARCHITECTURE.md, docs/ALGORITHMS.md,
docs/ASSUMPTIONS.md (K, thresholds, yield-loss factor, crop intervals, commission
rate, all flagged "assumption, not calibrated"), docs/API.md, docs/DEMO_SCRIPT.md
(3 minutes: story > cobweb before/after > Gaon Brain re-plan > voice sale >
Sinchai/Claim Kit > shock chain > adoption slider > close), docs/DECISIONS.md,
docs/LIMITATIONS.md, docs/FEEDBACK.md, docs/PROGRESS.md, CHANGELOG.md,
.env.example, LICENSE (MIT).

## 11. SCRIPTS
make setup | seed | dev | test | lint | reset-demo, plus scripts/dev.py as the
cross-platform equivalent. `make dev` must give a working app with seeded data.

## 12. PHASES (each ends with the CHECKPOINT PROTOCOL in section 1)
P0 scaffold: repo, skeletons, tooling, Makefile, dev.py, AGENTS.md, doc stubs.
P1 data: models, event store, projections, seed data, providers with fallbacks.
P2 Ek Awaaz: voice parser, confirm loop, endpoints, 30+ tests, logbook page,
   Bhav Tulna, Awaaz Mode screen.
P3 Glut Guard: algorithm, property tests, Gaon Plan page with SVG map, Kyun?.
P4 Simulation: cobweb, adoption sweep, shock sim, backtest, before/after charts,
   adoption slider.
P5 Gaon Sanjha: tractor, bijli window, irrigation slots, Sinchai Card.
P6 Gaon Radar: reports, alerts, heatmap, Fasal Doctor photo flow.
P7 Gaon Bazaar and productivity: lots, commitments, payments, buyer trust,
   benchmark, Season Report.
P8 Khata Suraksha: Claim Kit (with PDF), Kharid Check, Mitra mode.
P9 Shock chain: /shock and the animated Jhatka panel wiring every pillar.
P10 Polish: design pass against section 7, accessibility, Playwright smoke,
   README and all docs, final tag v1.0.0.

## 13. DEFINITION OF DONE
- `make setup && make dev` works on a clean checkout, no keys, no internet.
- The 3-minute demo in docs/DEMO_SCRIPT.md runs without errors.
- All tests pass; ruff, mypy, tsc, eslint clean.
- Every simulated number is labelled; assumptions visible in UI and docs.
- Screenshots reviewed; nothing violates the FORBIDDEN list in section 7.
- Clean git log, tags present, PROGRESS.md fully checked.
- Final message lists what is real, what is simulated, known gaps.

## 14. NON-GOALS
User authentication beyond a role picker, real payments, real SMS/IVR/missed-call,
cloud deployment, native apps, any submission to government or insurer systems.