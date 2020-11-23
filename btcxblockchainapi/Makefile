.PHONY: initdb install test server

initdb:
	python3 manage.py migrate

install: export PIPENV_VENV_IN_PROJECT = 1
install:
	pip3 install pipenv
	python3 -m pipenv install --skip-lock

test:
	python3 manage.py test --verbosity 2

server:
	python3 manage.py runserver 0.0.0.0:8000
