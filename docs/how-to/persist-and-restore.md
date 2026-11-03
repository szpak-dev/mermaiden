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
[`src/mermaiden/runtime/snapshot/schema.v10.json`](../../src/mermaiden/runtime/snapshot/schema.v10.json). Earlier and
unknown versions are rejected; Mermaiden does not guess a migration.

Draft diagrams may be snapshotted and restored. A snapshot recorded as valid is checked again during restoration, while
malformed envelopes, unknown identities, and invalid typed values fail at the persistence boundary.

`classDiagram` and `treeView-beta` do not support standalone annotation objects. Snapshots containing class notes or
TreeView annotations are rejected. Class stereotypes such as `interface` and `abstract`, stored in a class element's
`annotations` field, remain supported. Other diagram kinds retain their annotation capabilities.

To migrate a version-9 snapshot explicitly, keep a backup and work on a copy:

1. For `classDiagram` and `treeView-beta`, replace the top-level `annotations` collection with an empty list.
   This discards standalone notes, icons, descriptions, and highlights stored as annotation objects. Preserve nested class
   `annotations` fields: those contain UML stereotypes.
2. Set the envelope's `version` to `10` for every diagram kind. Preserve all other fields, including explicit layout
   choices. To adopt ELK for a migrated class diagram, configure its layout as `elk` after restoration.
3. Restore the copy with `application.restore(...)`, review its rendered output, then persist a fresh
   `application.snapshot(restored).to_dict()` result.

Version 10 rejects every version-9 snapshot until explicitly migrated, including snapshots without annotations and
snapshots of other diagram kinds. Older versions require their own migration before these steps apply.

Use `snapshot_contract_identity(diagram_id)` when another component needs the current identity of one diagram contract:

```python
from mermaiden import Application

with Application.create() as application:
    identity = application.snapshot_contract_identity("classDiagram")
```

Treat that identity as a contract value, not as a Python import instruction.
