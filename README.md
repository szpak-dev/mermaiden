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
from mermaiden import Application

application = Application.create()
diagrams = application.available_diagrams()
print(diagrams)
```

`Application.available_diagrams()` returns the supported diagram catalog. `Application.diagram_info(diagram_id)` returns the typed diagram API for an individual syntax. CLI workflows are available through `python -m mermaiden.cli`.

## Application API

`Application` is the boundary for API and persistence adapters. Create a diagram by Mermaid syntax id, apply a named domain command, and persist the JSON-safe snapshot returned by the application.

```python
from mermaiden import Application
from mermaiden.application import DiagramCommand

application = Application.create()
diagram = application.create_diagram("sequenceDiagram")
application.apply(diagram, DiagramCommand("add_participant", {"id": "api", "label": "API"}))

payload = application.snapshot(diagram).to_dict()
restored = application.restore(payload)
source = application.render(restored)
```

Before committing a revision, callers can require Mermaid's complete rendering and layout phase to produce an SVG. The report is non-mutating and identifies the compatible Mermaid version together with structured diagnostics on failure.

```python
report = application.validate_render(restored)
if not report.success:
    raise RuntimeError(report.diagnostics)
svg = report.svg
```

Snapshots have a versioned envelope and may be stored as JSON. `Application.restore()` validates restored state before returning it. Command argument values use the diagram operation names; JSON string values are accepted for enum arguments.

The caller can discover the REST contract without maintaining a manifest. `diagram_description()` returns JSON Schema for the diagram's elements, relations, annotations, and commands. `command_payload()` returns the generated Pydantic request model for one command.

```python
description = application.diagram_description("sequenceDiagram")
payload_type = application.command_payload("sequenceDiagram", "add_participant")
payload = payload_type.model_validate({"id": "api", "kind": "control"})
```

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
