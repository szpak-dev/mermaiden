.PHONY: docs docs-check test verify

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

test:
	PYTHONPATH=src .venv/bin/python -m new_proto.fixtures
	PYTHONPATH=src .venv/bin/python -m new_proto.preview .dev/.preview/*.mmd --output .preview/index.html
	open .preview/index.html

verify: docs-check
	uv run ruff check .
	uv run pyright
	uv run pytest
