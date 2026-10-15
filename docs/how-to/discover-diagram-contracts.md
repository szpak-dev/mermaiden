# Discover diagram contracts

Use discovery when an adapter or tool needs to build a UI, validate command input, or expose Mermaiden without
maintaining its own diagram inventory.

## List supported diagrams

```python
from mermaiden import Application

with Application.create() as application:
    diagrams = application.available_diagrams()
    identifiers = tuple(diagram.id for diagram in diagrams)
```

Each `DiagramInfo` identifies one runtime-registered Mermaid syntax. Pass its `id` back to the application rather than
deriving package or class names.

## Read one diagram contract

```python
from mermaiden import Application

with Application.create() as application:
    description = application.diagram_description("classDiagram")
    operations = tuple(description.commands)
```

The description owns the discoverable element, relation, annotation, and command schemas for that diagram.

## Validate command arguments

```python
from mermaiden import Application

with Application.create() as application:
    payload_contract = application.command_payload("sequenceDiagram", "add_participant")
    payload = payload_contract.validate({"id": "api", "label": "API", "kind": "control"})

    assert payload.values["kind"] == "control"
```

Validation converts external JSON-shaped values once at the application boundary. Submit the resulting values under the
same operation name with `execute()` or `apply_batch()`.

For the generated mutation inventory, including update, move, reorder, and retarget coverage, use the
[diagram contracts reference](../reference/contracts.md).
