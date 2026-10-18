# FRONTEND AUDIT

## Current Pages & Buttons

| Page | Route | Buttons | Wired to API? | Works? | Notes |
|------|-------|---------|---------------|--------|-------|
| Ek Awaaz | `/awaaz` | Mic (Web Speech), Typed input (Enter), Haan, Nahi | Yes (voice/parse, voice/confirm, logbook) | Partial | Mic works, typed input works, confirm works, but UI is raw (pre tag for transcript), no ledger table, no Bhav Tulna chip, no "Awaaz Mode" toggle |
| Gaon Plan | `/plan` | Run Plan, Kyun? | Yes (glut/plan) | Partial | SVG map is hardcoded 3 rects, no real plot data, Kyun? shows raw JSON, no plan vs baseline cards, no adoption slider, no cobweb chart |
| Gaon Sanjha | `/sanjha` | Load (tractor) | Yes (tractor/schedule) | Partial | Only tractor schedule loads, bijli window and sinchai card are static text |
| Gaon Radar | `/radar` | Analyze (Fasal Doctor) | Yes (doctor/analyze) | Partial | File upload + select + analyze works, alerts empty, no heatmap, no report form |
| Gaon Bazaar | `/bazaar` | Load Lots | Yes (bazaar/lots) | Partial | Only loads lots, other sections are static text |
| Khata Suraksha | `/suraksha` | Load Sinchai, Generate Claim Kit PDF | Yes (suraksha/sinchai, suraksha/claim/pdf) | Partial | Sinchai loads, PDF generates, other sections static |
| Simulation | `/simulation` | None (slider only) | No | Broken | Slider does nothing, canvas empty, no API calls |
| Jhatka | `/jhatka` | Blight, Heavy rain, Price drop | Yes (shock) | Partial | Buttons work, chain shows text, no animated pillar updates, no map recolouring |

## App Shell Issues
- No persistent header with app name, Sample data badge, language toggle
- Navigation uses raw NavLink with inline styles, no active state styling
- No mobile bottom nav / desktop side rail
- No 3-line strip (Samasya / Hamara jawab / Aaj ka asar) on any page
- No loading / error / empty states anywhere
- Colors don't match the solid pastel spec (uses old palette)
- No Hindi/English toggle
- Awaaz Mode toggle missing

## API Endpoints Used
- `/voice/parse` ✅
- `/voice/confirm` ✅
- `/logbook` ✅
- `/glut/plan` ✅
- `/tractor/schedule` ✅
- `/doctor/analyze` ✅
- `/bazaar/lots` ✅
- `/suraksha/sinchai` ✅
- `/suraksha/claim/pdf` ✅
- `/shock` ✅

## Missing API Endpoints Needed
- `/glut/apply` - for applying plan
- `/glut/state` - for current plan state
- `/power/window` - for bijli window
- `/water/slots` - for water slots
- `/radar/report` - for disease/animal reports
- `/radar/alerts` - for alerts list
- `/radar/heatmap` - for heatmap data
- `/bazaar/commitments`, `/bazaar/payments`, `/bazaar/buyers` - for Bazaar
- `/suraksha/kharid`, `/suraksha/claim` - for Suraksha
- `/sim/cobweb`, `/sim/adoption` - for Simulation
- `/shock` with detailed effects per pillar - for Jhatka animation

## Summary
**Working pages**: Awaaz (partial), Plan (partial), Sanjha (partial), Radar (partial), Suraksha (partial), Jhatka (partial)
**Broken/Placeholder pages**: Simulation, Bazaar (mostly placeholder), Suraksha (mostly placeholder)
**Navigation**: All 8 pages in nav, but 3 are mostly broken

**Decision per brief**: Keep Awaaz, Plan, Sanjha, Radar, Jhatka in nav. Remove Bazaar, Suraksha, Simulation from nav for now (or mark as coming soon).