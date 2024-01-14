#
# Makefile for setting up env, running app, testing, deploying
#

.PHONY: all env checkenv run help

VERSION := $(shell head -n 10 CHANGELOG.md | grep -Eo "[0-9\.]+" | head -n 1)
PYTHON := python3

all: checkenv help

auth/bin/activate:
	@echo "creating python venv 'auth'"
	$(PYTHON) -m venv auth
auth/.pip_installed: auth/bin/activate requirements.txt
	@echo "installing python dependencies"
	bash -c "source auth/bin/activate && $(PYTHON) -m pip install -r requirements.txt"
	touch $@

env: auth/bin/activate auth/.pip_installed env.sh

checkenv:
	@[ "${VIRTUAL_ENV}" ] || ( echo error: environment not set, please run 'source env.sh'; exit 1 )
	@[ "${GOT_API_SECRETS}" ] || ( echo error: secrets not set, please setup 'secrets.sh'; exit 1 )

run: checkenv
	@echo "running any new database migrations"
	flask db upgrade
	@echo "running api server"
	waitress-serve --host 127.0.0.1 app.app:app

dev: checkenv
	@echo "running any new database migrations"
	flask db upgrade
	@echo "running api server"
	flask run

help:
	@echo "targets:"
	@echo "  help: show this help menu"
	@echo "  env: setup python venv"
	@echo "  run: run flask api server"
	@echo "  dev: run flask api server in debug mode"
	@echo
	@echo "variables:"
	@echo "  PYTHON               $(PYTHON)"
	@echo "  VERSION              $(VERSION)"
	@echo "  VIRTUAL_ENV          $(VIRTUAL_ENV)"
	@echo "  GOT_API_SECRETS      $(GOT_API_SECRETS)"
	@echo "  FLASK_APP            $(FLASK_APP)"
