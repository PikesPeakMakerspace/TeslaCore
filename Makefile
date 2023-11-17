#
# Makefile for setting up env, running app, testing, deploying
#

.PHONY: all env run help

VERSION := $(shell head -n 10 CHANGELOG.md | grep -Eo "[0-9\.]+" | head -n 1)
PYTHON := python3

all: env help

auth/bin/activate:
	@echo "creating python venv 'auth'"
	$(PYTHON) -m venv auth
auth/.pip_installed: auth/bin/activate requirements.txt
	@echo "installing python dependencies"
	bash -c "source auth/bin/activate && $(PYTHON) -m pip install -r requirements.txt"
	touch $@

env: auth/bin/activate auth/.pip_installed env.sh

ifndef VIRTUAL_ENV
$(error environment not set, please run 'source env.sh')
endif
ifndef GOT_API_SECRETS
$(error secrets not set, please setup 'secrets.sh')
endif

run: env
	@echo "running api server"
	flask run

help:
	@echo "targets:"
	@echo "  help: show this help menu"
	@echo "  env: setup python venv"
	@echo "  run: run flask api server"
	@echo
	@echo "variables:"
	@echo "  PYTHON               $(PYTHON)"
	@echo "  VERSION              $(VERSION)"
	@echo "  VIRTUAL_ENV          $(VIRTUAL_ENV)"
	@echo "  GOT_API_SECRETS      $(GOT_API_SECRETS)"
	@echo "  FLASK_APP            $(FLASK_APP)"
