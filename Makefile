.PHONY: docs docs-check test verify

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

test:
	PYTHONPATH=src .venv/bin/python -m new_proto.application fixtures
	PYTHONPATH=src .venv/bin/python -m new_proto.application preview --output .preview/index.html
	mkdir -p .preview/.validation
	result=0; for file in .preview/*.mmd; do npx --yes --package=@mermaid-js/mermaid-cli mmdc -i "$$file" -o ".preview/.validation/$$(basename "$$file" .mmd).svg" || result=1; done; exit $$result
	open .preview/index.html

verify: docs-check
	uv run ruff check .
	uv run pyright
	uv run pytest
