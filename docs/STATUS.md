# Gaon Brain (गाँव ब्रेन) - Status Audit

**Date:** 2026-10-18  
**Repository Location:** `c:\Users\Daksh\OneDrive\Desktop\gaon-brain\gaon-brain`  
**Current Git Commit:** `2350b78 wip: before moving to antigravity`  
**Git Branch:** `master`  
**Git Remote:** None configured (`origin` not set)

---

## 1. Executive Summary

Gaon Brain has an existing initial scaffold with FastAPI, SQLModel/SQLite, and React+Vite+TypeScript. Many backend modules and frontend pages were stubbed out during initial prototyping, but several core algorithms are hardcoded placeholders, database transactions are not linked to endpoints, and the frontend currently builds a legacy static HTML file instead of the React application.

This audit evaluates the codebase strictly against the hackathon project brief and defines an honest, verified baseline of what works, what is partial, and what is broken.

---

## 2. What Works (Verified & Tested)

- **Backend Pytest Suite (13 tests passing):**
  - Pytest runs and passes inside `backend/`: `tests/test_bazaar.py`, `tests/test_glut.py`, `tests/test_p1.py`, `tests/test_radar.py`, `tests/test_sanjha.py`, `tests/test_shock_sim.py`, `tests/test_suraksha.py`, `tests/test_voice.py`.
- **Database Schema & Models:**
  - `SQLModel` definitions for `Village`, `Farmer`, `Plot`, `Event`, `Sale`, `Buyer`, `Lot`, `Commitment`, `TractorRequest`, `PowerLog`, `WaterSlot`, `Plan`, `PlanItem`, `Report`, `Claim`, `Purchase`, `Consent`.
  - Database initialization `init_db()` creates tables in SQLite cleanly.
  - `claim_pdf.py` renders a PDF dossier with ReportLab and bundled Noto Sans Devanagari font.
- **Basic Voice Intent & Parsing:**
  - Regex and keyword intent classifier for 9 core intents (`record_sale`, `power_on`, `power_off`, `animal_sighting`, `disease_report`, `tractor_request`, `sowing_plan`, `irrigation_done`, `loss_report`).
  - Number parsing for English and transliterated Hindi number words (`ek` through `sau`, `hazar`, `dedh`, `sadhe`, `paune`).
  - Unit multipliers for `kilo`/`kg`, `quintal` (100 kg), and `maund` (40 kg).
  - Crop fuzzy matching for `wheat`, `rice`, `mustard`, `chana`, `gehun`, `dhan`, `sarson`.
- **Core Greedy Glut Planner Algorithm:**
  - Greedy sequential crop-week assignment with downward-sloping linear demand curve ($P(S) = P_0 \cdot (1 - K \cdot (S/D - 1))$ clipped between $0.3 P_0$ and $1.8 P_0$).
  - Floor check: if a plot's planned profit is lower than its baseline, it retains the baseline so `farmers_worse_off == 0`.
- **Distance Calculation:**
  - Haversine distance formula implemented in `app/radar.py`.
- **Disease Demo Provider:**
  - `DiseaseProvider.analyze` returns structured condition and confidence.
- **Frontend Tooling:**
  - TypeScript compiler (`tsc`) and Vite build succeed without TypeScript errors.

---

## 3. What is Partial (Incomplete or Missing Integration)

- **Voice Parser & Confirm Flow (`app/voice.py`, `app/routers_voice.py`):**
  - **Missing crop:** "aalu" / "potato" (the exact crop used in the prompt example `"500 kilo aalu, 10 rupay kilo, Sharma ji ko"`) is not in `CROPS`.
  - **Missing rate extraction:** Rates like "10 rupay kilo" or "20 rupaye" are not extracted, preventing automatic total calculation (`qty_kg * rate`).
  - **Missing Devanagari script parsing:** Hindi digits (०-९) and Devanagari words (e.g., "५०० किलो आलू") are not parsed.
  - **No Database Persistence:** `/voice/confirm` only returns in-memory state; it does not write to the SQLite `Sale`, `Event`, or `logbook` table.
  - **Tests incomplete:** `test_voice.py` duplicates 12 intent sentences 3 times to reach 36 items; does not verify quantity, units, rates, or Hindi script.
- **Glut Guard Planner (`app/glut.py`, `app/routers_glut.py`):**
  - `GET /glut/state` returns mock `{"status": "ok"}` without reading current village plots or active plan from the database.
  - `POST /glut/plan` and `POST /glut/apply` require explicit request payload rather than pulling the seeded village plots if none provided.
  - `POST /glut/apply` does not save the plan items to the database.
  - Per-plot "Kyun?" explanations are hardcoded strings (`"crop=... week=...; expected profit vs baseline"`) rather than meaningful Hindi/English explanations.
  - Does not compute max crop share before vs. after.
  - Property test suite asserting `farmers_worse_off == 0` across randomized seeds is not yet implemented.
- **Seeded Plot Polygons (`app/seed.py`):**
  - Plots are seeded with `polygon="[]"` (empty). There are no real polygon coordinates for rendering a village field/khasra map.
- **Tractor Scheduler (`app/sanjha.py`):**
  - Only sorts requests by `(prev_served_count, want_date)`.
  - Does not assign tractors to hours/capacity, does not implement clash-to-next-day shift, and does not calculate peak daily demand with vs. without staggered sowing.

---

## 4. What is Broken or Stubbed

- **Frontend React Entry (`frontend/index.html`):**
  - `frontend/index.html` was not updated during the React migration: it lacks `<div id="root"></div>` and `<script type="module" src="/src/main.tsx"></script>`.
  - When `npm run build` is executed, Vite builds the old legacy HTML file and does NOT bundle `App.tsx` or React!
- **Simulation Module (`app/sim.py`):**
  - Functions `cobweb`, `adoption_sweep`, `shock`, `backtest` are 2-line stubs returning static mock dictionaries (e.g. `{"note": "lag applied"}`).
  - **No endpoints exist:** `/sim/cobweb`, `/sim/adoption`, `/sim/shock` are not routed in FastAPI.
- **Electricity (Bijli) Window (`app/sanjha.py`, `app/routers_sanjha.py`):**
  - Hardcoded response `{"window": "06:00-09:00", "confidence": "sample"}`; does not read `power_logs` from DB or compute hourly $P(\text{on}) = \text{on\_days} / \text{total\_days}$ over contiguous 3-hour windows.
- **Irrigation Slots (`app/sanjha.py`, `app/routers_sanjha.py`):**
  - Hardcoded response `[{"plot_id": p["id"], "slot": "morning"}]`; does not account for village pump-hour budget, crop water interval, days since irrigation, or plot health.
- **Gaon Radar Alerts & Heatmap (`app/radar.py`, `app/routers_radar.py`):**
  - `alerts()` and `heatmap()` return empty lists `[]`.
  - No threshold clustering ($\ge N$ reports within $R$ km in $D$ days).
  - No heatmap grid calculation with recency decay.
  - `POST /radar/report` does not save reports or events to SQLite.
- **Shock Chain (`app/shock.py`, `app/routers_shock.py`):**
  - Returns hardcoded array `["Radar", "Yield", "Bazaar", "Glut re-plan", "Sanjha rebalance"]` and empty `kyun: []`.
  - Does not mutate plot health, trigger re-planning, re-balance water slots, or generate per-farmer impacts.
- **API Mounting & Deployment Architecture:**
  - API routes are mounted directly at root (`/voice`, `/glut`, etc.) instead of `/api/...`.
  - Health check is `/health` instead of `/api/health`.
  - Backend does not serve the built frontend at `/` with SPA fallback.
  - Database does not auto-seed on startup when empty (requires manual seed).
  - No `render.yaml` specification for single-service deployment.
- **Frontend Design & Pages:**
  - `index.css` has drop shadows and gradient variables from a previous commit, violating the strict solid pastel specification.
  - Navigation links to placeholder pages (`Bazaar`, `Suraksha`, `Simulation`) containing non-functional controls (dead buttons, unlinked range slider, blank canvas). Per project instructions, dead items must be removed from navigation.
  - Missing 3-line strip ("समस्या", "हमारा जवाब", "आज का असर") on every screen.
  - Missing persistent header with "नमूना डेटा / Sample data" badge and Hindi/English language toggle.
  - Missing mobile bottom tab bar and desktop side rail.
  - Village map in Plan page is 3 hardcoded SVG rects instead of real plot polygons colored by crop.
  - Missing adoption slider and cobweb before/after chart on Plan screen.
  - Awaaz screen lacks ruled ledger table, mandi price comparison chip, and dedicated "Awaaz Mode" view.
  - Jhatka screen lacks animated 5-step propagation chain and map recoloring.
- **Dev Runner Scripts:**
  - `scripts/dev.py` and `Makefile` contain trailing literal `EOF` characters.
  - `scripts/dev.py` invokes `npm` directly without `shell=True` on Windows, causing subprocess failures.

---

## 5. Commands to Run & Test

### Backend
- **Run pytest suite:**
  ```powershell
  cd backend
  python -m pytest tests
  ```
- **Run seed script:**
  ```powershell
  cd backend
  python -m app.seed
  ```
- **Run backend development server (port 8000):**
  ```powershell
  cd backend
  python -m uvicorn app.main:app --reload --port 8000
  ```

### Frontend
- **Install dependencies:**
  ```powershell
  cd frontend
  cmd /c "npm install"
  ```
- **Run frontend development server (port 5173):**
  ```powershell
  cd frontend
  cmd /c "npm run dev"
  ```
- **Build frontend:**
  ```powershell
  cd frontend
  cmd /c "npm run build"
  ```

### Full-Stack Single Runner
- Once Step 2 is implemented, backend serves frontend at `http://localhost:8000`:
  ```powershell
  cd frontend && cmd /c "npm run build"
  cd ../backend && python -m uvicorn app.main:app --reload --port 8000
  ```

---

## 6. Git Status & Remote Notice

- The repository is at `c:\Users\Daksh\OneDrive\Desktop\gaon-brain\gaon-brain`.
- Current branch: `master`.
- **Note:** `git remote` has no `origin` URL configured in this clone. Running `git push origin HEAD` currently returns:
  `fatal: 'origin' does not appear to be a git repository`.
- We will commit locally after every step with conventional commit messages. Once you add your remote via `git remote add origin <url>`, pushes will succeed directly.

---

## 7. Proposed Order of Execution

In strict accordance with the user instructions, the plan is structured as follows:

- [ ] **Step 0: Audit (Current)**
  - Write `docs/STATUS.md` detailing exact state, verified capabilities, and gaps.
  - Stop and wait for user's "go".
- [ ] **Step 1: Backend Core Implementation & Testing**
  - Implement full Voice parser with Hindi/Hinglish, Devanagari numerals, aalu/potato support, rate parsing, and DB ledger event logging in `voice_confirm`. Expand test suite to $\ge 30$ distinct sentences.
  - Implement real Glut Guard planner with dynamic DB seeding, max crop share calculation, and rich Hindi/English "Kyun?" explanations.
  - Implement property test suite verifying `farmers_worse_off == 0` and max crop share non-increasing across randomized seeds.
  - Implement real Simulation engine (cobweb model, adoption sweep $\alpha \in \{0, 0.3, 0.6, 1.0\}$, shock simulation) and mount `/sim/*` endpoints.
  - Implement real Tractor scheduler with daily hours capacity and clash-to-next-day shift.
  - Implement real Electricity (Bijli) window algorithm computing hourly $P(\text{on})$ over 3-hour windows from `power_logs`.
  - Implement fair Irrigation slot assignment considering pump-hour budgets, crop intervals, and plot health.
  - Implement Radar alert clustering ($\ge N$ reports within $R$ km in $D$ days) and 2D spatial heatmap with recency weighting.
  - Implement dynamic Shock chain endpoint: propagating disease/rain/price drop through Radar $\rightarrow$ Yield $\rightarrow$ Bazaar $\rightarrow$ Glut re-plan $\rightarrow$ Sanjha rebalance with per-farmer "Kyun?" impacts.
  - Add realistic polygon coordinates to seeded village plots for map visualization.
  - Run all backend tests to ensure 100% pass rate. Commit.
- [ ] **Step 2: Deploy-Ready Packaging**
  - Mount all API routes under `/api` with `GET /api/health` returning `{"status": "ok"}`.
  - Fix `frontend/index.html` to properly mount React root and bundle `/src/main.tsx`.
  - Serve built frontend (`frontend/dist`) directly from FastAPI backend at `/` with SPA catch-all fallback.
  - Auto-seed database on startup if SQLite database is empty.
  - Create unified multi-stage `Dockerfile`, `.dockerignore`, and `render.yaml` configured for Render free tier.
  - Test locally by building frontend, launching backend, and validating single-URL access at `http://localhost:8000`.
  - Commit.
- [ ] **Step 3: Frontend Screens (Solid Pastel Design & API Wiring)**
  - Clean up navigation: focus exclusively on the core pillars (Plan, Awaaz, Sanjha, Radar, Jhatka); remove broken/placeholder routes (`Bazaar`, `Suraksha`, `Simulation` page merged into Plan).
  - Enforce design tokens: cream `#FAF6EE`, ink `#243040`, mint `#BDE5CC`, peach `#FFD3B5`, lavender `#D5CBF0`, sky `#BFE0F5`, butter `#FFEDA8`, rose `#F7C6D0`, 2px solid ink borders, no shadows/gradients. Add mobile bottom nav & desktop side rail. Add Hindi/English language toggle and "नमूना डेटा / Sample data" badge.
  - Add standard 3-line strip on all screens: "समस्या", "हमारा जवाब", "आज का असर".
  - Wire loading, error with retry, and empty states on all screens.
  - **Screen 3a - गाँव प्लान (Home):** SVG village cadastral map colored by crop, crop-share bars, "प्लान लगाओ" button, plan vs baseline cards, per-plot "क्यों?" drawer, adoption slider, and before/after cobweb chart.
  - **Screen 3b - एक आवाज़:** Web Speech API (hi-IN) big mic button, typed fallback, confirm card with हाँ/नहीं, ruled ledger table ("बही-खाता"), mandi price chip ("भाव तुलना"), and dedicated "आवाज़ मोड" toggle.
  - **Screen 3c - झटका:** Interactive shock triggers (blight, rain, price drop), animated 5-step propagation chain, per-farmer "क्यों?" lines, and dynamic map recoloring.
  - **Screen 3d - गाँव संझा:** Tractor calendar, electricity window probability chart, irrigation slots, and per-plot Sinchai करो/मत करो decision card.
  - **Screen 3e - गाँव रडार:** Disease/animal report form, photo upload with confidence score (if $< 70\%$ shows "विशेषज्ञ से पूछो"), live alerts list, and SVG heatmap overlay.
  - Test and verify each screen with backend endpoints. Commit.
- [ ] **Step 4: Documentation**
  - Update `README.md` with overview, 5-minute setup, demo path, architecture, and honest limitations.
  - Finalize `docs/DEMO_SCRIPT.md` (3-minute flow: story $\rightarrow$ cobweb before/after $\rightarrow$ plan $\rightarrow$ voice sale $\rightarrow$ shock chain $\rightarrow$ adoption slider).
  - Update `docs/ASSUMPTIONS.md` detailing all synthetic parameters.
  - Update `docs/LIMITATIONS.md` and add Render deployment instructions.
  - Commit.
- [ ] **Step 5: Final Check & Polish**
  - Review responsive layouts across mobile (390px) and desktop (1280px).
  - Ensure zero dead buttons, no fake data, no lorem ipsum, and clean startup with zero API keys required.
  - Commit.
