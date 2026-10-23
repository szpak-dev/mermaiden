.PHONY: application-test-freeze application-test-policy architecture ci compat compatibility configuration-proofs configuration-render-shard diagrams-preview diagrams-test diagrams-validate diagrams-validate-core documentation-check documentation-linkcheck documentation-links fast-check format integration integration-core mermaid-freshness mermaid-lock mermaid-sync mutation-contract mutation-contract-check package-check pytest quality renderer-install

UV := uv
RUN := $(UV) run --no-sync
PYTHON := $(RUN) python

architecture:
	@$(RUN) lint-imports --cache-dir .dev/import_linter_cache

compat:
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli compat

documentation-links:
	@$(PYTHON) scripts/check_docs_links.py

documentation-check: documentation-links
	@$(UV) pip install --requirement docs/requirements.lock
	@PYTHONPATH=src $(RUN) sphinx-build -W --keep-going -b html docs docs/_build/html

documentation-linkcheck:
	@$(UV) pip install --requirement docs/requirements.lock
	@PYTHONPATH=src $(RUN) sphinx-build -W --keep-going -b linkcheck docs docs/_build/linkcheck

mermaid-sync:
	@mermaid_version="$$(PYTHONPATH=src $(PYTHON) -c 'from mermaiden import Application; print(Application.create().mermaid_version)')"; \
	mermaid_cli_version="$$(PYTHONPATH=src $(PYTHON) -c 'from mermaiden import Application; print(Application.create().mermaid_cli_version)')"; \
	PUPPETEER_SKIP_DOWNLOAD=true npm install --save-dev --save-exact \
		"mermaid@$$mermaid_version" "@mermaid-js/mermaid-cli@$$mermaid_cli_version"

mermaid-freshness:
	@NPM_CONFIG_CACHE=.dev/npm-cache PYTHONPATH=src $(PYTHON) scripts/check_mermaid_freshness.py

mermaid-lock:
	@PYTHONPATH=src $(PYTHON) scripts/check_mermaid_lock.py

format:
	@$(RUN) ruff format .
	@$(RUN) ruff check --fix .

mutation-contract:
	@PYTHONPATH=src $(PYTHON) scripts/render_mutation_contract.py --write

mutation-contract-check:
	@PYTHONPATH=src $(PYTHON) scripts/render_mutation_contract.py --check

application-test-policy:
	@PYTHONPATH=src $(PYTHON) scripts/check_application_tests.py

application-test-freeze:
	@PYTHONPATH=src $(PYTHON) scripts/check_application_tests.py --check-freeze

package-check: renderer-install
	@set -eu; \
	temporary=$$(mktemp -d); \
	trap 'rm -rf "$$temporary"' EXIT; \
	artifacts="$$temporary/artifacts"; \
	mkdir -p "$$artifacts"; \
	$(UV) build --out-dir "$$artifacts"; \
	$(PYTHON) -m twine check "$$artifacts"/*; \
	cd "$$temporary"; \
	PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(UV) run --isolated --with "$$artifacts"/*.whl python -I "$(CURDIR)/scripts/smoke_installed_wheel.py" "$$artifacts"/*.tar.gz

quality:
	@$(RUN) ruff format --check .
	@$(RUN) ruff check .
	@$(RUN) pyright
	@$(MAKE) architecture
	@$(MAKE) application-test-freeze mermaid-lock mutation-contract-check

pytest:
	@$(RUN) pytest

fast-check:
	@$(MAKE) --jobs=3 quality pytest compat

renderer-install:
	@npm ci
	@npx puppeteer browsers install

integration: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration

integration-core: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration -k "not test_every_configuration_probe_produces_a_real_svg"

configuration-render-shard: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" PYTHONPATH=. $(PYTHON) scripts/check_configuration_rendering.py --shard $(SHARD)

diagrams-validate: integration

diagrams-validate-core: integration-core

diagrams-preview:
	@PYTHONPATH=. $(PYTHON) scripts/render_preview.py

diagrams-test: diagrams-preview
	@open .dev/preview/index.html

compatibility:
	@$(MAKE) compat
	@$(MAKE) diagrams-preview
	@$(MAKE) diagrams-validate

configuration-proofs:
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" PYTHONPATH=. $(PYTHON) scripts/render_configuration_proofs.py
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" PYTHONPATH=. $(PYTHON) scripts/render_c4_human_proofs.py

ci:
	@$(UV) lock --check
	@$(UV) sync --locked --group dev
	@$(MAKE) --jobs=5 quality pytest compatibility package-check documentation-check
