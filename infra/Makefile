#
# Makefile for setting up deployment env, sshing into deployment server
#

.PHONY: all checkenv vpn help

all: checkenv help

checkenv:
	@[ "${GOT_DEPLOY_ENV}" ] || ( echo error: deploy environment not set, please run 'source infra/deploy_env.sh'; exit 1 )
	@[ "${GOT_DEPLOY_SECRETS}" ] || ( echo error: deploy secrets not set, please setup 'infra/deploy_secret.sh'; exit 1 )

vpn: checkenv
	@echo "connect to the vpn"

help:
	@echo "targets:"
	@echo "  help: show this help menu"
	@echo "  vpn: connect to the vpn server"
	@echo "  ssh: ssh into the deploy server"
	@echo
	@echo "variables:"
	@echo "  GOT_DEPLOY_ENV       $(GOT_DEPLOY_ENV)"
	@echo "  GOT_DEPLOY_SECRETS   $(GOT_DEPLOY_SECRETS)"
