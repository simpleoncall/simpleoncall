STATIC=./simpleoncall/static
CLEANCSS=./node_modules/.bin/cleancss --s0 --source-map --output
PYTHON=/usr/bin/env python

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

clean: clean-css

runserver: migrate
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate
