STATIC=./simpleoncall/static
CLEANCSS=./node_modules/.bin/cleancss --s0 --source-map --output
UGLIFYJS=./node_modules/.bin/uglifyjs --source-map
PYTHON=/usr/bin/env python
CELERY=`which celery`

deps:
	pip install -r requirements.txt
	npm install

clean-deps:
	pip uninstall -r requirements.txt || true
	rm -rf node_modules || true

core-css:
	$(PYTHON) -c 'from simpleoncall.utils import print_stylesheets; print_stylesheets()' | xargs -t -L 1 $(CLEANCSS)

css: core-css

clean-css:
	rm $(STATIC)/css/core.min.*

js: core-js

core-js:
	$(PYTHON) -c 'from simpleoncall.utils import print_scripts; print_scripts()' | xargs -t -L 1 $(UGLIFYJS)

clean-js:
	rm $(STATIC)/js/core.min.*
	rm $(STATIC)/js/dashboard.min.*

clean: clean-css

runserver: migrate
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

worker:
	$(CELERY) -A simpleoncall worker -l info
