# API.md

Endpoints (prefix none, base http://127.0.0.1:8000):

Health: GET /health

Voice: POST /voice/parse, POST /voice/confirm
Bhav: GET /bhav/tulna?crop=&sold_rate=
Logbook: GET /logbook

Glut: GET /glut/state, POST /glut/plan, POST /glut/apply
Sim: (planned) POST /sim/cobweb, /sim/adoption, /sim/shock

Sanjha: POST /tractor/schedule, GET /power/window, POST /water/slots
Radar: POST /radar/report, POST /doctor/analyze, GET /radar/alerts, GET /radar/heatmap
Bazaar: GET /bazaar/lots, POST /bazaar/commit, GET /bazaar/payments, GET /bazaar/buyers
Suraksha: POST /suraksha/sinchai, /suraksha/kharid, /suraksha/claim
Shock: POST /shock

OpenAPI: /docs
EOF