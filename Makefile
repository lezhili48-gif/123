.PHONY: dev run-weekly test

dev:
	npm run dev

run-weekly:
	python services/backend/scripts/run_weekly.py

test:
	cd services/backend && pytest
