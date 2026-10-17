setup:
	python -m venv .venv
	.venv/Scripts/pip install -r backend/requirements.txt 2>/dev/null || .venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

seed:
	cd backend && python -m app.seed

dev:
	python scripts/dev.py &
	cd frontend && npm run dev

test:
	cd backend && python -m pytest -q

lint:
	cd backend && ruff check .

reset-demo:
	rm -f data/*.db data/mandi.csv
	make seed
EOF