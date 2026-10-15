# Create a sequence diagram

This walkthrough creates a typed sequence diagram, applies one atomic change, persists it, and renders Mermaid source.
The application discovers the supported command contract, so the example does not need a separate operation manifest.

## Install Mermaiden

Mermaiden requires Python 3.12 or later.

```sh
pip install mermaiden
```

Source generation needs no Node.js process or browser. Full SVG validation is a separate step covered in
[Render and validate Mermaid](../how-to/render-and-validate.md).

## Build the complete loop

Keep one application handle and one diagram through discovery, mutation, persistence, restoration, and rendering:

```python
from mermaiden import Application

with Application.create() as application:
    diagram_info = application.diagram_info("sequenceDiagram")
    description = application.diagram_description(diagram_info.id)
    assert "add_participant" in description.commands
    assert "add_message" in description.commands

    diagram = application.create_diagram(diagram_info.id)
    report = application.apply_batch(
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

    assert report.can_commit
    payload = application.snapshot(diagram).to_dict()
    restored = application.restore(payload)
    source = application.render(restored)

    assert application.snapshot(restored).to_dict() == payload
    assert "\nsequenceDiagram\n" in source
    assert "Client" in source
    assert "API" in source
    assert "Request" in source
```

`diagram_description()` is the live diagram contract. It describes objects, commands, and JSON-shaped payload schemas
from the same registry used by execution. The ordered batch is checked once and rolls back to the exact pre-batch
snapshot if it cannot commit. The restored diagram then renders the same valid typed state. The snapshot—not Mermaid
text—is therefore the durable boundary for continuing work.
