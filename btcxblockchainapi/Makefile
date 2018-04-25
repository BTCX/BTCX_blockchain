initdb:
	python3 manage.py migrate

install:
	pip3 install --upgrade setuptools
	pip3 install --upgrade -r requirements.txt

test:
	python3 manage.py test --verbosity 2

server:
	python3 manage.py runserver 0.0.0.0:8000