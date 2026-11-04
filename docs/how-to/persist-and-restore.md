# Persist and restore diagrams

Persist the dictionary returned by `DiagramSnapshot.to_dict()`. Do not serialize Python classes, import paths, or an
adapter-specific mirror of the diagram.

```python
import json

from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("pie")
    application.execute(diagram, "add_slice", {"id": "typed", "label": "Typed", "value": 70})
    application.execute(diagram, "add_slice", {"id": "other", "label": "Other", "value": 30})

    stored = json.dumps(application.snapshot(diagram).to_dict())
    restored = application.restore(json.loads(stored))

    assert application.render(restored) == application.render(diagram)
```

The envelope contains a snapshot version and registry-owned discriminators. The current schema is checked in at
[`src/mermaiden/runtime/snapshot/schema.v11.json`](../../src/mermaiden/runtime/snapshot/schema.v11.json).
Restoration accepts only snapshots matching the current schema version and registered type contracts.

Draft diagrams may be snapshotted and restored. A snapshot recorded as valid is checked again during restoration, while
malformed envelopes, unknown identities, and invalid typed values fail at the persistence boundary.

`classDiagram` and `treeView-beta` do not support standalone annotation objects. Snapshots containing class notes or
TreeView annotations are rejected. Class stereotypes such as `interface` and `abstract`, stored in a class element's
`annotations` field, are supported.

Use `snapshot_contract_identity(diagram_id)` when another component needs the current identity of one diagram contract:

```python
from mermaiden import Application

with Application.create() as application:
    identity = application.snapshot_contract_identity("classDiagram")
```

Treat that identity as a contract value, not as a Python import instruction.
