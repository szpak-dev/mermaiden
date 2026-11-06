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

## Upgrade historical snapshots

Use `Application.upgrade_snapshot(payload, allow_loss=False)` explicitly before restoring an older snapshot.
The operation supports source versions **6 through 11**, upgrading them to **12**. A valid v12 snapshot returns the
same JSON values with an empty change report. `restore()` continues to accept only the current contract.

| Source transition | Upgrade behavior |
| --- | --- |
| v6 to v7 | Validate the single generic-argument limit and preserve existing class types and argument order. |
| v7 to v8 | Expand configuration with fixed introduction values and encode the required wrappers. |
| v8 to v9 | Introduce theme, look, and layout; translate supported renderer selections into layouts. |
| v9 to v10 | Retire standalone Class and TreeView annotations with explicit loss acceptance. Preserve class stereotypes and explicit layouts. |
| v10 to v11 | Retire the Class `html_labels` field and report its original value. |
| v11 to v12 | Convert unambiguous Packet ranges and bit counts to tagged positions; introduce Flowchart step settings. |

Version 11 is an intermediate historical contract, rather than a separately tagged package release.

```python
from mermaiden import Application, SnapshotUpgradeError

with Application.create() as application:
    try:
        result = application.upgrade_snapshot(payload)
    except SnapshotUpgradeError as error:
        print(error.paths)
        for change in error.changes:
            print(change.paths, change.description, change.discarded)
        raise

    restored = application.restore(result.snapshot.to_dict())
    for change in result.changes:
        print(change.paths, change.description)
```

`payload` is the dictionary loaded from storage. Each `SnapshotChange` contains JSON Pointer `paths`, a `description`,
`discarded` original values keyed by their original pointers, and `requires_loss_acceptance`.
Inspect the proposed changes before choosing `allow_loss=True`. That option permits the documented removals: nonempty
standalone Class or TreeView annotations, and enabled Class HTML labels. Retiring `html_labels=False` is reported but
does not require loss acceptance. Fields introduced and retired inside the upgrade are not reported as lost caller data.

The input stays untouched on success and failure. Upgrades preserve identifiers, relationships, ordering, stereotypes,
and supported explicit configuration. Unknown fields or types, unsupported versions, invalid annotation targets,
ambiguous Packet coordinates, and values requiring implicit normalization raise `SnapshotUpgradeError`, even when loss
is allowed. Persisted titles or date formats incompatible with current constraints also fail; they are not repaired.
Successful results pass current restoration without rendering, network access, or filesystem writes.
