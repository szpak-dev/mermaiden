.PHONY: ci compat diagrams-test diagrams-validate format mutation-contract package-check

VENV := .venv
PYTHON := $(VENV)/bin/python

$(PYTHON):
	python3 -m venv $(VENV)

compat: $(PYTHON)
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli compat

diagrams-validate: $(PYTHON)
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli fixtures --output .dev/preview
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli preview --output .dev/preview/index.html
	@mkdir -p .dev/preview/.validation
	@: > .dev/preview/.validation/diagrams.md; for file in .dev/preview/*.mmd; do printf '## %s\n\n```mermaid\n' "$$(basename "$$file" .mmd)" >> .dev/preview/.validation/diagrams.md; awk '1' "$$file" >> .dev/preview/.validation/diagrams.md; printf '```\n\n' >> .dev/preview/.validation/diagrams.md; done
	@npx --yes --package=@mermaid-js/mermaid-cli mmdc -i .dev/preview/.validation/diagrams.md -o .dev/preview/.validation/diagrams.rendered.md
	@index=1; for file in .dev/preview/*.mmd; do mv ".dev/preview/.validation/diagrams.rendered-$$index.svg" ".dev/preview/.validation/$$(basename "$$file" .mmd).svg"; index=$$((index + 1)); done
	@! rg -q 'Syntax error in text|Parse error|UnknownDiagramError|TypeError' .dev/preview/.validation --glob '*.svg'

diagrams-test: diagrams-validate
	open .dev/preview/index.html

format: $(PYTHON)
	@$(PYTHON) -m ruff format .
	@$(PYTHON) -m ruff check --fix .

mutation-contract: $(PYTHON)
	@PYTHONPATH=src $(PYTHON) scripts/render_mutation_contract.py --write

package-check: $(PYTHON)
	@set -eu; \
	temporary=$$(mktemp -d); \
	trap 'rm -rf "$$temporary"' EXIT; \
	artifacts="$$temporary/artifacts"; \
	environment="$$temporary/environment"; \
	mkdir -p "$$artifacts"; \
	$(PYTHON) -m build --outdir "$$artifacts"; \
	$(PYTHON) -m twine check "$$artifacts"/*; \
	$(PYTHON) -m venv "$$environment"; \
	"$$environment/bin/python" -m pip install --no-cache-dir "$$artifacts"/*.whl; \
	"$$environment/bin/python" -m pip check; \
	cd "$$temporary"; \
	"$$environment/bin/python" -I "$(CURDIR)/scripts/smoke_installed_wheel.py"

ci: $(PYTHON)
	@$(PYTHON) -m ensurepip --upgrade
	@$(PYTHON) -m pip install -e ".[dev]"
	@$(PYTHON) -m ruff format --check .
	@$(PYTHON) -m ruff check .
	@$(PYTHON) -m pyright
	@$(PYTHON) -m pytest
	@$(MAKE) compat
	@$(MAKE) diagrams-validate
	@$(MAKE) package-check
