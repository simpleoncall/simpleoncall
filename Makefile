PYTHON=/usr/bin/env python
CELERY=`which celery`

deps:
	pip install -r requirements.txt

clean-deps:
	pip uninstall -r requirements.txt || true

runserver: migrate
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

worker:
	$(CELERY) -A simpleoncall worker -l info
