.PHONY: install & run clean

install:
	pip install -r requirements.txt
	
environment:
	@echo "> Creating venv"; \
	python3 -m venv .venv; \
	. .venv/bin/activate; \
	echo "> Installing requirements"; \
	.venv/bin/python -m pip install --upgrade pip; \
	make install;
run:
	. .venv/bin/activate; \
	python app.py;