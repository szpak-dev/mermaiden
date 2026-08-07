.PHONY: compat docs docs-check test verify

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

compat:
	@PYTHONPATH=src .venv/bin/python -m new_proto.application compat

test:
	@PYTHONPATH=src .venv/bin/python -m new_proto.application fixtures
	@PYTHONPATH=src .venv/bin/python -m new_proto.application preview --output .preview/index.html
	@mkdir -p .preview/.validation
	@: > .preview/.validation/diagrams.md; for file in .preview/*.mmd; do printf '## %s\n\n```mermaid\n' "$$(basename "$$file" .mmd)" >> .preview/.validation/diagrams.md; awk '1' "$$file" >> .preview/.validation/diagrams.md; printf '```\n\n' >> .preview/.validation/diagrams.md; done
	@npx --yes --package=@mermaid-js/mermaid-cli mmdc -i .preview/.validation/diagrams.md -o .preview/.validation/diagrams.rendered.md
	@index=1; for file in .preview/*.mmd; do mv ".preview/.validation/diagrams.rendered-$$index.svg" ".preview/.validation/$$(basename "$$file" .mmd).svg"; index=$$((index + 1)); done
	@! rg -q 'Syntax error in text|Parse error|UnknownDiagramError|TypeError' .preview/.validation --glob '*.svg'
	open .preview/index.html

verify: docs-check
	uv run ruff check .
	uv run pyright
	uv run pytest
