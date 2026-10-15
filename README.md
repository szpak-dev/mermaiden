# Mermaiden

Mermaiden generates deterministic Mermaid source from typed Python diagram models. It gives applications a discoverable
diagram catalog, strict semantic commands, atomic mutations, versioned snapshots, and optional full SVG validation.

The package produces Mermaid text rather than owning its presentation. Render that text in a Markdown viewer, a browser,
or your own Mermaid CLI workflow.

## Documentation

- [Documentation entrance](docs/index.md)
- [Tutorials](docs/tutorials/index.md)
- [How-to guides](docs/how-to/index.md)
- [Explanation](docs/explanation/index.md)
- [Architecture and ownership](docs/architecture/index.md)
- [Glossary](docs/glossary/index.md)
- [Technical reference](docs/reference/index.md)

## Installation

Python 3.12 or later is required.

```sh
pip install mermaiden
```

Source generation needs no browser or Mermaid executable. `Application.validate_render()` additionally requires the
compatible `mmdc` executable and a browser.

## Discover a diagram contract

<!-- executable-example:discovery:start -->
```python
from mermaiden import Application

with Application.create() as application:
    diagrams = application.available_diagrams()
    sequence = application.diagram_info("sequenceDiagram")
    description = application.diagram_description(sequence.id)
    payload_contract = application.command_payload(sequence.id, "add_participant")
    payload = payload_contract.validate({"id": "api", "label": "API", "kind": "control"})

    assert sequence in diagrams
    assert "add_participant" in description.commands
    assert payload.values["kind"] == "control"
```
<!-- executable-example:discovery:end -->

`Application.available_diagrams()` returns the runtime catalog. `diagram_description()` and `command_payload()` expose
the same strict contracts used by command execution, so an adapter does not need a parallel operation manifest.

## Create, persist, and render

<!-- executable-example:application:start -->
```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("sequenceDiagram")
    change = application.apply_batch(
        diagram,
        (
            {"operation": "add_participant", "arguments": {"id": "client", "label": "Client"}},
            {"operation": "add_participant", "arguments": {"id": "api", "label": "API"}},
            {
                "operation": "add_message",
                "arguments": {
                    "id": "request",
                    "source_id": "client",
                    "target_id": "api",
                    "label": "Request",
                },
            },
        ),
    )
    assert change.can_commit

    payload = application.snapshot(diagram).to_dict()
    restored = application.restore(payload)
    source = application.render(restored)
```
<!-- executable-example:application:end -->

Snapshots use a closed, versioned envelope with registry-owned identities rather than Python import paths. Drafts may be
persisted and restored, but rendering requires every blocking constraint to be resolved. See
[Persist and restore diagrams](docs/how-to/persist-and-restore.md) for the exact boundary.

To validate the generated source as SVG, first follow the consumer setup in
[Render and validate Mermaid](docs/how-to/render-and-validate.md).

## Update, move, and reorder

<!-- executable-example:mutations:start -->
```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("block")
    application.execute(diagram, "add_group", {"id": "source", "label": "Source"})
    application.execute(diagram, "add_group", {"id": "target", "label": "Target"})
    application.execute(
        diagram,
        "add_block",
        {"id": "catalog", "label": "Catalog", "parent_id": "source"},
    )
    application.execute(
        diagram,
        "update_element",
        {"id": "catalog", "kind": "block_node", "changes": {"label": "Product Catalog"}},
    )
    application.execute(
        diagram,
        "move_element",
        {"id": "catalog", "kind": "block_node", "parent_id": "target", "position": 0},
    )
    snapshot = application.snapshot(diagram).to_dict()
    restored = application.restore(snapshot)
    assert application.render(restored) == application.render(diagram)
```
<!-- executable-example:mutations:end -->

The
[generated mutation contract](docs/contracts/diagram-mutations/README.md)
records update, move, reorder, and retarget semantics and per-diagram coverage. Use
[Mutate diagrams](docs/how-to/mutate-diagrams.md) for task-focused mutation, removal, and atomic-rejection guidance.

## Development

Create the development environment and run the fast tier:

```sh
uv sync --locked --group dev
make fast-check
```

The [contribution guide](CONTRIBUTING.md) covers repository verification and generated contracts. Documentation is built
strictly with `make documentation-check`; external links are checked with `make documentation-linkcheck`.

## License

Mermaiden is proprietary software. No permission to use, copy, modify, or distribute it is granted without prior express
written permission. See [LICENSE](LICENSE) for the complete terms.
