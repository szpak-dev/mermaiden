.PHONY: application-test-freeze application-test-policy architecture ci compat compatibility configuration-proofs configuration-render-shard diagrams-preview diagrams-test diagrams-validate diagrams-validate-core documentation-check documentation-linkcheck documentation-links fast-check format integration integration-core mermaid-freshness mermaid-lock mermaid-sync mutation-contract mutation-contract-check package-check pytest quality renderer-install

UV := uv
RUN := $(UV) run --no-sync
PYTHON := $(RUN) python

architecture:
	@$(RUN) lint-imports --cache-dir .dev/import_linter_cache

compat:
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli compat

documentation-links:
	@$(RUN) pytest tests/repository/test_documentation.py::test_documentation_links_resolve_and_every_page_is_reachable

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
	@NPM_CONFIG_CACHE=.dev/npm-cache $(RUN) pytest -m freshness tests/repository/test_mermaid_versions.py

mermaid-lock:
	@$(RUN) pytest tests/repository/test_mermaid_versions.py::test_node_dependencies_match_public_supported_versions

format:
	@$(RUN) ruff format .
	@$(RUN) ruff check --fix .

mutation-contract:
	@PYTHONPATH=src $(PYTHON) scripts/render_mutation_contract.py --write

mutation-contract-check:
	@$(RUN) pytest tests/repository/test_documentation.py::test_generated_mutation_contract_matches_public_discovery

application-test-policy:
	@$(RUN) pytest tests/repository/test_application_policy.py::test_product_tests_use_public_gates_and_cover_public_operations

application-test-freeze:
	@$(RUN) pytest tests/repository/test_application_policy.py::test_verification_inputs_match_the_accepted_freeze

package-check: renderer-install
	@set -eu; \
	temporary=$$(mktemp -d); \
	trap 'rm -rf "$$temporary"' EXIT; \
	artifacts="$$temporary/artifacts"; \
	mkdir -p "$$artifacts"; \
	$(UV) build --out-dir "$$artifacts"; \
	$(PYTHON) -m twine check "$$artifacts"/*; \
	set -- "$$artifacts"/*.tar.gz; \
	export MERMAIDEN_SDIST="$$1"; \
	cd "$$temporary"; \
	PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(UV) run --isolated --no-project --with "$$artifacts"/*.whl --with pytest --with playwright \
		python -I -m pytest -c "$(CURDIR)/pyproject.toml" -o "cache_dir=$$temporary/pytest-cache" \
		-m "not freshness and not configuration_render and not caller_snapshots" "$(CURDIR)/tests/installed" \
		"$(CURDIR)/tests/mermaiden/contracts/test_png_rendering.py" \
		"$(CURDIR)/tests/mermaiden/contracts/test_exported_svg_labels.py" \
		"$(CURDIR)/tests/mermaiden/contracts/test_mutation_conformance.py" \
		"$(CURDIR)/tests/mermaiden/contracts/test_application.py" \
		"$(CURDIR)/tests/mermaiden/contracts/test_updates.py"

quality:
	@$(RUN) ruff format --check .
	@$(RUN) ruff check .
	@$(RUN) pyright
	@$(MAKE) architecture

pytest:
	@$(RUN) pytest

fast-check:
	@$(MAKE) --jobs=3 quality pytest compat

renderer-install:
	@npm ci
	@npx puppeteer browsers install
	@$(RUN) playwright install chromium --no-shell

integration: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m integration

integration-core: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(PYTHON) -m pytest -m "integration and not configuration_render"

configuration-render-shard: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" $(RUN) pytest -m configuration_render \
		"tests/mermaiden/contracts/test_configuration_rendering.py::test_configuration_probes_produce_valid_svg_in_order[$(SHARD)]"

diagrams-validate: integration

diagrams-validate-core: integration-core

diagrams-preview: renderer-install
	@PATH="$(CURDIR)/node_modules/.bin:$$PATH" PYTHONPATH=. $(PYTHON) scripts/render_preview.py

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
