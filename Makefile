# Use one shell for all commands in a target recipe
.ONESHELL:
# Set default goal
.DEFAULT_GOAL := help
# Use bash shell in Make instead of sh
SHELL := /bin/bash
# Charm variables
CHARM_NAME := megaraid-check
CHARM_STORE_URL := cs:~huntdatacenter/megaraid-check
CHARM_HOMEPAGE := https://github.com/huntdatacenter/charm-megaraid-check/
CHARM_BUGS_URL := https://github.com/huntdatacenter/charm-megaraid-check/issues
CHARM_BUILD_DIR := /tmp/charm-builds
CHARM_PATH := $(CHARM_BUILD_DIR)/$(CHARM_NAME)


lint: ## Run linter
	tox -e lint


build: ## Build charm
	tox -e build


deploy: ## Deploy charm
	juju deploy $(CHARM_BUILD_DIR)/$(CHARM_NAME)


upgrade: ## Upgrade charm
	juju upgrade-charm $(CHARM_NAME) --path $(CHARM_BUILD_DIR)/$(CHARM_NAME)


force-upgrade: ## Force upgrade charm
	juju upgrade-charm $(CHARM_NAME) --path $(CHARM_BUILD_DIR)/$(CHARM_NAME) --force-units


test-xenial: ## Test xenial deployment
	tox -e test-xenial


test-bionic: ## Test bionic bundle
	tox -e test-bionic


push: clean build generate-repo-info ## Push charm to stable channel
	@echo "Publishing $(CHARM_STORE_URL)"
	@export rev=$$(charm push $(CHARM_PATH) $(CHARM_STORE_URL) 2>&1 \
		| tee /dev/tty | grep url: | cut -f 2 -d ' ') \
	&& charm release --channel stable $$rev \
	&& charm grant $$rev --acl read everyone \
	&& charm set $$rev extra-info=$$(git rev-parse --short HEAD) \
		bugs-url=$(CHARM_BUGS_URL) homepage=$(CHARM_HOMEPAGE)


clean: ## Clean .tox and build
	@echo "Cleaning files"
	@if [ -d $(CHARM_PATH) ] ; then rm -r $(CHARM_PATH) ; fi
	@if [ -d .tox ] ; then rm -r .tox ; fi


# Internal targets
clean-repo:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo '!!! Hard resetting repo and removing untracked files !!!'; \
		git reset --hard; \
		git clean -fdx; \
	fi

generate-repo-info:
	@if [ -f $(CHARM_PATH)/repo-info ] ; then rm -r $(CHARM_PATH)/repo-info ; fi
	@echo "commit: $$(git rev-parse HEAD)" >> $(CHARM_PATH)/repo-info
	@echo "commit-short: $$(git rev-parse --short HEAD)" >> $(CHARM_PATH)/repo-info
	@echo "branch: $$(git rev-parse --abbrev-ref HEAD)" >> $(CHARM_PATH)/repo-info
	@echo "remote: $$(git config --get remote.origin.url)" >> $(CHARM_PATH)/repo-info
	@echo "generated: $$(date -u)" >> $(CHARM_PATH)/repo-info


# Display target comments in 'make help'
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
