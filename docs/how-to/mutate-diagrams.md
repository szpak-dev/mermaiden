# Mutate diagrams

Use named commands to change a diagram. Commands validate JSON-shaped arguments before dispatch and preserve diagram
object identity across updates, moves, and reorders.

## Execute one command

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("block")
    application.execute(diagram, "add_group", {"id": "services", "label": "Services"})
    application.execute(
        diagram,
        "add_block",
        {"id": "catalog", "label": "Catalog", "parent_id": "services"},
    )
```

`execute()` is convenient when each intermediate result is valid or when the selected diagram permits a draft at that
point.

## Apply dependent commands together

Use `apply_batch()` when several operations form one logical change:

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("block")
    report = application.apply_batch(
        diagram,
        (
            {"operation": "add_group", "arguments": {"id": "services", "label": "Services"}},
            {
                "operation": "add_block",
                "arguments": {"id": "catalog", "label": "Catalog", "parent_id": "services"},
            },
        ),
    )
    assert report.can_commit
```

The batch is ordered and atomic. Mermaiden restores the exact original snapshot after invalid arguments, an unknown
operation, a command failure, or a final constraint failure.

## Update, move, and reorder

The common mutation commands use stable object IDs and an explicit concrete `kind`:

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("block")
    application.execute(diagram, "add_group", {"id": "source", "label": "Source"})
    application.execute(diagram, "add_group", {"id": "target", "label": "Target"})
    application.execute(diagram, "add_block", {"id": "catalog", "label": "Catalog", "parent_id": "source"})
    application.execute(diagram, "add_block", {"id": "pricing", "label": "Pricing", "parent_id": "source"})
    application.execute(diagram, "add_block", {"id": "inventory", "label": "Inventory", "parent_id": "source"})

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
    application.execute(
        diagram,
        "reorder_elements",
        {"parent_id": "source", "element_ids": ["inventory", "pricing"]},
    )
```

Reordering requires the exact current members of one collection. Moving preserves the complete subtree and rejects
containment cycles.

## Remove objects safely

Elements, relations, and annotations have separate removal commands. Removing an element without `cascade=True` is
rejected when descendants, relations, or annotations still depend on it. Rejection leaves the complete snapshot
unchanged. With `cascade=True`, Mermaiden removes the diagram-defined subtree plus every dependent relation and
annotation as one atomic change:

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("sequenceDiagram")
    application.execute(diagram, "add_box", {"id": "group", "label": "Group"})
    application.execute(
        diagram,
        "add_participant",
        {"id": "client", "label": "Client", "box_id": "group"},
    )
    application.execute(diagram, "add_participant", {"id": "api", "label": "API"})
    application.execute(
        diagram,
        "add_message",
        {"id": "request", "source_id": "client", "target_id": "api", "label": "Request"},
    )
    before = application.snapshot(diagram).to_dict()

    try:
        application.execute(diagram, "remove_element", {"id": "group"})
    except RuntimeError:
        pass
    else:
        raise AssertionError("unsafe removal unexpectedly succeeded")
    assert application.snapshot(diagram).to_dict() == before

    report = application.execute(diagram, "remove_element", {"id": "group", "cascade": True})
    assert report is not None and report.accepted
    assert tuple((item.kind, item.id) for item in report.removed) == (
        ("element", "group"),
        ("element", "client"),
        ("relation", "request"),
    )
```

`remove_relation` also requires explicit cascading when annotations target that relation. `remove_annotation` has no
dependants and needs only its `id`. Discover each strict payload with `command_payload()` before exposing it through an
adapter.

The [generated mutation contract](../contracts/diagram-mutations/README.md) is the authority for update, move, reorder,
and retarget applicability and field classification. Removal is a catalog command whose dependency behavior is described
above and by its discoverable payload.
