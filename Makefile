.PHONY: install & run clean

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
run:
	python app.py