.PHONY: help dev prod build-docker-image run-docker-image unittest

CONT_NAME ?= "age_gender_detector"
PORT ?= 5101

help: Makefile
	@echo

dev:
	python app.py

prod:
	uwsgi --plugins http,python --http :$(PORT) --wsgi-file app.py --callable app

build-docker-image:
	docker build . -t $(CONT_NAME)

run-docker-image:
	docker rm --force $(CONT_NAME) || echo ""
	docker run -d -p $(PORT):5101 --name $(CONT_NAME) --restart always $(CONT_NAME)

dev-docker-compose:
	virtualenv venv
	venv/bin/pip3 install -r requirements.txt
	venv/bin/python app.py

unittest:
	python -m unittest

