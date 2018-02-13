initdb:
	# python manage.py syncdb
	python manage.py migrate

install:
	pip install --upgrade --user setuptools
	pip install --upgrade --user -r requirements.txt
	pip install --upgrade --user sherlock

test:
	python manage.py test --verbosity 2

server:
	python manage.py runserver 0.0.0.0:8000