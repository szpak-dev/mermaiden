# Diagram contract reference

A diagram contract is the complete discoverable description of one registered syntax: its objects, commands, payload
schemas, placements, and persisted identity. The generated mutation contract below is one focused part of that larger
runtime contract.

Mermaiden publishes generated, repository-owned reference material for every registered diagram:

- The [diagram mutation contract](../contracts/diagram-mutations/README.md) defines update, move, reorder, retarget,
  no-op, and atomic rejection semantics.
- Its per-diagram matrices describe which elements, relations, and annotations support each public operation.
- The [character-policy matrices](../contracts/diagram-mutations/characters/README.md) record the accepted character
  rules for command string fields.

These files are generated from public `Application` discovery and contract semantics. Regenerate them with
`make mutation-contract`; do not maintain a second handwritten inventory here.

## Recursive class member types

The `classDiagram` command schemas use one recursive `ClassType` value for attribute types, method parameter types, and
method return types. `name` is the outer named type. `arguments` is an ordered sequence of nested `ClassType` values and
defaults to an empty sequence. There is no one-argument limit, so mappings, tuples, and deeper combinations retain their
declared order:

```python
from mermaiden import Application

with Application.create() as application:
    payload = application.command_payload("classDiagram", "add_class")
    arguments = payload.validate(
        {
            "id": "catalog",
            "label": "Catalog",
            "attributes": [
                {
                    "name": "items",
                    "type": {
                        "name": "Map",
                        "arguments": [
                            {"name": "Key"},
                            {"name": "List", "arguments": [{"name": "Value"}]},
                        ],
                    },
                }
            ],
            "methods": [
                {
                    "name": "find",
                    "parameters": [{"name": "key", "type": {"name": "Key"}}],
                    "return_type": {
                        "name": "Pair",
                        "arguments": [{"name": "Key"}, {"name": "Value"}],
                    },
                }
            ],
        }
    )

    attribute_type = arguments.values["attributes"][0]["type"]
    return_type = arguments.values["methods"][0]["return_type"]
    assert attribute_type["arguments"][1]["arguments"][0]["name"] == "Value"
    assert tuple(item["name"] for item in return_type["arguments"]) == ("Key", "Value")
```

Snapshot and restore preserve the same recursive values, and Mermaid rendering formats every nested argument in order.
