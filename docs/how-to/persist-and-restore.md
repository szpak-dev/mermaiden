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
[`src/mermaiden/runtime/snapshot/schema.v12.json`](../../src/mermaiden/runtime/snapshot/schema.v12.json).
Restoration accepts only snapshots matching the current schema version and registered type contracts.

Draft diagrams may be snapshotted and restored. A snapshot recorded as valid is checked again during restoration, while
malformed envelopes, unknown identities, and invalid typed values fail at the persistence boundary.
Forbidden parent-child placements are rejected even in draft snapshots. Stored titles permit the initial empty value
and otherwise follow the shared text policy; Gantt date formats use the same policy as their command input.

Packet fields have one `position`: `{"kind": "range", "start": 0, "end": 7}` or `{"kind": "bits", "bits": 8}`.
Use `update_element` with `changes.position` to replace the complete position atomically. Ranges have nonnegative,
ordered endpoints; bit counts are positive. `add_field` and `add_bits` create these same values, and an omitted
`add_field` end denotes a single bit.

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
