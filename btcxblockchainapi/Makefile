initdb:
	python manage.py migrate

install:
	pip install --upgrade setuptools
	pip install --upgrade -r requirements.txt

test:
	python manage.py test --verbosity 2

server:
	python manage.py runserver 0.0.0.0:8000