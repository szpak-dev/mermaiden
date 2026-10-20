.PHONY: architecture ci compat compatibility configuration-proofs configuration-render-shard diagrams-preview diagrams-test diagrams-validate diagrams-validate-core documentation-check documentation-linkcheck documentation-links fast-check format integration integration-core mermaid-sync mutation-contract package-check pytest quality

UV := uv
RUN := $(UV) run --no-sync
PYTHON := $(RUN) python
CONFIGURATION_RENDER_TEST := tests/fixtures/test_configuration_proofs.py::test_every_configuration_probe_produces_a_real_svg

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
	PUPPETEER_SKIP_DOWNLOAD=true npm install --save-dev --save-exact "@mermaid-js/mermaid-cli@$$mermaid_version"

format:
	@$(RUN) ruff format .
	@$(RUN) ruff check --fix .

mutation-contract:
	@PYTHONPATH=src $(PYTHON) scripts/render_mutation_contract.py --write

package-check:
	@set -eu; \
	temporary=$$(mktemp -d); \
	trap 'rm -rf "$$temporary"' EXIT; \
	artifacts="$$temporary/artifacts"; \
	mkdir -p "$$artifacts"; \
	$(UV) build --out-dir "$$artifacts"; \
	$(PYTHON) -m twine check "$$artifacts"/*; \
	cd "$$temporary"; \
	$(UV) run --isolated --with "$$artifacts"/*.whl python -I "$(CURDIR)/scripts/smoke_installed_wheel.py" "$$artifacts"/*.tar.gz

quality:
	@$(RUN) ruff format --check .
	@$(RUN) ruff check .
	@$(RUN) pyright
	@$(MAKE) architecture

pytest:
	@$(RUN) pytest

fast-check:
	@$(MAKE) --jobs=3 quality pytest compat

integration:
	@PUPPETEER_SKIP_DOWNLOAD=true npm ci
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration

integration-core:
	@PUPPETEER_SKIP_DOWNLOAD=true npm ci
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration -k "not test_every_configuration_probe_produces_a_real_svg"

configuration-render-shard:
	@PUPPETEER_SKIP_DOWNLOAD=true npm ci
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration "$(CONFIGURATION_RENDER_TEST)[shard-$(SHARD)-of-4]"

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
