.PHONY: install & run clean

install:
	pip install -r requirements.txt
	
environment:
	@echo "> Creating venv"; \
	python3 -m venv .venv; \
	. .venv/bin/activate; \
	echo "> Installing requirements"; \
	.venv/bin/python -m pip install --upgrade pip; \
	.venv/bin/pip install -r requirements.dev.txt;
run:
	python app.py