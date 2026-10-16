# Build a contract-driven adapter

An adapter sits between JSON-shaped input and a typed diagram. It should discover Mermaiden's live contract instead of
maintaining a second command inventory, and it must not leave partial state behind when one request is unsafe.

This walkthrough discovers a sequence-diagram command, proves that a dangling reference leaves the diagram unchanged,
then accepts a complete request and carries it through persistence and rendering.

## Discover, reject, and recover

```python
from mermaiden import Application

with Application.create() as application:
    description = application.diagram_description("sequenceDiagram")
    assert "add_message" in description.commands

    message_schema = application.command_payload("sequenceDiagram", "add_message").schema()
    assert "target_id" in message_schema["properties"]

    diagram = application.create_diagram("sequenceDiagram")
    before = application.snapshot(diagram).to_dict()
    rejected = (
        {"operation": "add_participant", "arguments": {"id": "client", "label": "Client"}},
        {
            "operation": "add_message",
            "arguments": {
                "id": "request",
                "source_id": "client",
                "target_id": "missing",
                "label": "Request",
            },
        },
    )

    try:
        application.apply_batch(diagram, rejected)
    except RuntimeError as error:
        assert "unknown element 'missing'" in str(error)
    else:
        raise AssertionError("invalid adapter request unexpectedly succeeded")

    assert application.snapshot(diagram).to_dict() == before

    accepted = (
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
    )
    report = application.apply_batch(diagram, accepted)
    assert report.can_commit

    payload = application.snapshot(diagram).to_dict()
    restored = application.restore(payload)
    source = application.render(restored)
    assert "Client" in source and "API" in source and "Request" in source
```

The failed batch creates no participant and no message because `apply_batch()` restores the exact pre-request snapshot.
The accepted batch uses the same JSON-shaped boundary, but its complete reference set can commit. The adapter can
persist the returned snapshot and treat Mermaid source as output rather than as its data model.
