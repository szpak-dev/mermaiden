.PHONY: ci compat diagrams-test diagrams-validate format mutation-contract

VENV := .venv
PYTHON := $(VENV)/bin/python

$(PYTHON):
	python3 -m venv $(VENV)

compat: $(PYTHON)
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli compat

diagrams-validate: $(PYTHON)
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli fixtures
	@PYTHONPATH=src $(PYTHON) -m mermaiden.cli preview --output .preview/index.html
	@mkdir -p .preview/.validation
	@: > .preview/.validation/diagrams.md; for file in .preview/*.mmd; do printf '## %s\n\n```mermaid\n' "$$(basename "$$file" .mmd)" >> .preview/.validation/diagrams.md; awk '1' "$$file" >> .preview/.validation/diagrams.md; printf '```\n\n' >> .preview/.validation/diagrams.md; done
	@npx --yes --package=@mermaid-js/mermaid-cli mmdc -i .preview/.validation/diagrams.md -o .preview/.validation/diagrams.rendered.md
	@index=1; for file in .preview/*.mmd; do mv ".preview/.validation/diagrams.rendered-$$index.svg" ".preview/.validation/$$(basename "$$file" .mmd).svg"; index=$$((index + 1)); done
	@! rg -q 'Syntax error in text|Parse error|UnknownDiagramError|TypeError' .preview/.validation --glob '*.svg'

diagrams-test: diagrams-validate
	open .preview/index.html

format: $(PYTHON)
	@$(PYTHON) -m ruff format .
	@$(PYTHON) -m ruff check --fix .

mutation-contract: $(PYTHON)
	@$(PYTHON) scripts/render_mutation_contract.py --write

ci: $(PYTHON)
	@$(PYTHON) -m ensurepip --upgrade
	@$(PYTHON) -m pip install -e ".[dev]"
	@$(PYTHON) -m ruff format --check .
	@$(PYTHON) -m ruff check .
	@$(PYTHON) -m pyright
	@$(PYTHON) -m pytest
	@$(MAKE) compat
	@$(MAKE) diagrams-validate
	@output=$$(mktemp -d); $(PYTHON) -m build --outdir "$$output" && $(PYTHON) -m twine check "$$output"/*
