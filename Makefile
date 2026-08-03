.PHONY: test smoke run

test:
	python -m pytest tests/unit tests/contract

smoke:
	python scripts/smoke_structure.py
	python scripts/smoke_packages.py
	python scripts/smoke_internal_api.py

run:
	uvicorn opticargo_agents.api:app --host 0.0.0.0 --port 8000
