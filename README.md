# mermaiden

`mermaiden` generates deterministic Mermaid source from typed Python diagram models. It supports the Mermaid syntax families registered by the package and validates each diagram before rendering its text.

The package produces Mermaid text only. Render it with Mermaid in a browser, Markdown viewer, or your own CLI workflow.

## Installation

Python 3.12 or later is required.

```sh
pip install mermaiden
```

## Quick start

```python
from mermaiden.application import Application

application = Application.create()
source = application.rendered_diagrams()["flowchart"]
print(source)
```

`Application.available_diagrams()` returns the supported diagram catalog. `Application.diagram_info(diagram_id)` returns the typed diagram API for an individual syntax.

## Development

The repository uses a single host-mode CI target:

```sh
make ci
```

It installs the development dependencies, runs linting, type checks, tests, compatibility validation, Mermaid CLI rendering, and wheel validation. To open the locally generated diagram preview, run:

```sh
make diagrams-test
```

## Release

Releases are versioned by annotated `vX.Y.Z` tags. After `make ci` passes, create and push the tag, then publish the GitHub release:

```sh
git tag -a v2.0.0 -m "v2.0.0"
git push origin v2.0.0
gh release create v2.0.0 --verify-tag --generate-notes --title v2.0.0
```
