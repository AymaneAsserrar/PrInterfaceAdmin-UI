.PHONY: install & run clean

environment: ## Configure venv & dev requirements
	(\
		echo "> Creating venv"; \
		python3 -m venv .venv; \
		source .venv/bin/activate; \
		echo "> Installing requirements"; \
		python -m pip install --upgrade pip; \
		pip install -r requirements.txt; \
	)
run:
	python app.py