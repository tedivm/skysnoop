SHELL := /bin/bash
PACKAGE_SLUG=adsblol
ifdef CI
	PYTHON_PYENV :=
	PYTHON_VERSION := $(shell python --version|cut -d" " -f2)
else
	PYTHON_PYENV := pyenv
	PYTHON_VERSION := $(shell cat .python-version)
endif
PYTHON_SHORT_VERSION := $(shell echo $(PYTHON_VERSION) | grep -o '[0-9].[0-9]*')

ifeq ($(USE_SYSTEM_PYTHON), true)
	PYTHON_PACKAGE_PATH:=$(shell python -c "import sys; print(sys.path[-1])")
	PYTHON_ENV :=
	PYTHON := python
	PYTHON_VENV :=
else
	PYTHON_PACKAGE_PATH:=.venv/lib/python$(PYTHON_SHORT_VERSION)/site-packages
	PYTHON_ENV :=  . .venv/bin/activate &&
	PYTHON := . .venv/bin/activate && python
	PYTHON_VENV := .venv
endif

# Used to confirm that pip has run at least once
PACKAGE_CHECK:=$(PYTHON_PACKAGE_PATH)/build
PYTHON_DEPS := $(PACKAGE_CHECK)


.PHONY: all
all: $(PACKAGE_CHECK)

.PHONY: install
install: $(PYTHON_PYENV) $(PYTHON_VENV) pip

.venv:
	python -m venv .venv

.PHONY: pyenv
pyenv:
	pyenv install --skip-existing $(PYTHON_VERSION)

.PHONY: pip
pip: $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]

$(PACKAGE_CHECK): $(PYTHON_VENV)
	$(PYTHON) -m pip install -e .[dev]

.PHONY: pre-commit
pre-commit:
	pre-commit install

#
# Formatting
#
.PHONY: chores
chores: ruff_fixes black_fixes dapperdata_fixes tomlsort_fixes

.PHONY: ruff_fixes
ruff_fixes:
	$(PYTHON) -m ruff check . --fix

.PHONY: black_fixes
black_fixes:
	$(PYTHON) -m ruff format .

.PHONY: dapperdata_fixes
dapperdata_fixes:
	$(PYTHON) -m dapperdata.cli pretty . --no-dry-run

.PHONY: tomlsort_fixes
tomlsort_fixes:
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") -i

#
# Testing
#
.PHONY: tests
tests: install pytest ruff_check black_check mypy_check dapperdata_check tomlsort_check

.PHONY: pytest
pytest:
	$(PYTHON) -m pytest --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: pytest_loud
pytest_loud:
	$(PYTHON) -m pytest --log-cli-level=DEBUG -log_cli=true --cov=./${PACKAGE_SLUG} --cov-report=term-missing tests

.PHONY: pytest_live
pytest_live:
	$(PYTHON) -m pytest tests/integration/test_live_api.py --run-live-api -v

.PHONY: ruff_check
ruff_check:
	$(PYTHON) -m ruff check

.PHONY: black_check
black_check:
	$(PYTHON) -m ruff format . --check

.PHONY: mypy_check
mypy_check:
	$(PYTHON) -m mypy ${PACKAGE_SLUG}

.PHONY: dapperdata_check
dapperdata_check:
	$(PYTHON) -m dapperdata.cli pretty .

.PHONY: tomlsort_check
tomlsort_check:
	$(PYTHON_ENV) toml-sort $$(find . -not -path "./.venv/*" -name "*.toml") --check

#
# OpenAPI Client Generation
#

.PHONY: openapi-download
openapi-download:
	@echo "Downloading OpenAPI spec from api.adsb.lol..."
	@mkdir -p resources
	curl -s https://api.adsb.lol/api/openapi.json > resources/openapi_spec.json
	@echo "Spec downloaded to resources/openapi_spec.json"

.PHONY: openapi-generate
openapi-generate: $(PYTHON_VENV)
	@echo "Generating OpenAPI models from spec..."
	datamodel-codegen \
		--input resources/openapi_spec.json \
		--output adsblol/models/openapi/generated.py \
		--target-python-version 3.10 \
		--output-model-type pydantic_v2.BaseModel \
		--field-constraints \
		--use-double-quotes \
		--use-standard-collections \
		--use-schema-description \
		--reuse-model \
		--collapse-root-models \
		--snake-case-field \
		--use-default
	@echo "Updating version tracking..."
	@VERSION=$$(cat resources/openapi_spec.json | python -c "import sys, json; print(json.load(sys.stdin)['info']['version'])"); \
	HASH=$$(shasum -a 256 resources/openapi_spec.json | cut -d' ' -f1); \
	DATE=$$(date +%Y-%m-%d); \
	echo '"""OpenAPI specification version tracking.' > adsblol/client/openapi_version.py; \
	echo '' >> adsblol/client/openapi_version.py; \
	echo 'This file is auto-generated and should not be edited manually.' >> adsblol/client/openapi_version.py; \
	echo 'Updated via: make openapi-update' >> adsblol/client/openapi_version.py; \
	echo '"""' >> adsblol/client/openapi_version.py; \
	echo '' >> adsblol/client/openapi_version.py; \
	echo '# Version from OpenAPI spec' >> adsblol/client/openapi_version.py; \
	echo "OPENAPI_VERSION = \"$$VERSION\"" >> adsblol/client/openapi_version.py; \
	echo '' >> adsblol/client/openapi_version.py; \
	echo '# SHA256 hash of the OpenAPI spec file' >> adsblol/client/openapi_version.py; \
	echo "SPEC_HASH = \"$$HASH\"" >> adsblol/client/openapi_version.py; \
	echo '' >> adsblol/client/openapi_version.py; \
	echo '# Last update timestamp' >> adsblol/client/openapi_version.py; \
	echo "SPEC_UPDATED = \"$$DATE\"" >> adsblol/client/openapi_version.py
	@echo "Models generated in adsblol/models/openapi/generated.py"

.PHONY: openapi-update
openapi-update: openapi-download openapi-generate
	@echo ""
	@echo "✓ OpenAPI models updated"
	@echo "Next steps:"
	@echo "  1. Review changes: git diff adsblol/models/openapi/"
	@echo "  2. Update client methods if endpoints changed"
	@echo "  3. Run tests: make pytest"
	@echo "  4. Consider: copilot @.github/prompts/update-openapi-client.prompt.md"

#
# Packaging
#

.PHONY: build
build: $(PACKAGE_CHECK)
	$(PYTHON) -m build
