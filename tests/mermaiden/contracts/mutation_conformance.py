import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from mermaiden import Application

MATRIX_ROOT = Path(__file__).resolve().parents[3] / "docs" / "contracts" / "diagram-mutations" / "diagrams"


@dataclass(frozen=True)
class MutationObject:
    kind: str
    fields: Mapping[str, object]
    parent_id: str | None = None
    position: int | None = None


@dataclass(frozen=True)
class ElementCollection:
    parent_id: str
    element_ids: tuple[str, ...]


def assert_mutation_conformance(application: Application, snapshot: Mapping[str, object]) -> None:
    payload = _mapping(json.loads(json.dumps(snapshot)))
    diagram_id = cast(str, payload["kind"])
    matrix = _json(MATRIX_ROOT / f"{diagram_id}.json")
    description = application.diagram_description(diagram_id)
    diagram = application.restore(payload)

    element_kinds = _snapshot_kinds(description.elements)
    elements, collections = _elements(payload["elements"], element_kinds, "")
    categorized = (
        ("elements", elements),
        ("relations", _objects(payload["relations"], _snapshot_kinds(description.relations))),
        ("annotations", _objects(payload["annotations"], _snapshot_kinds(description.annotations))),
    )
    for category, objects in categorized:
        cases: dict[str, MutationObject] = {}
        for item in objects:
            cases.setdefault(item.kind, item)
        contracts = _mapping(matrix[category])
        assert set(cases) == set(contracts), (
            f"{diagram_id} {category}: missing {set(contracts).difference(cases)}, "
            f"unexpected {set(cases).difference(contracts)}"
        )

        for kind, value in contracts.items():
            contract = _mapping(value)
            item = cases[kind]
            for field_name, classification in _mapping(contract["fields"]).items():
                if classification != "updateable":
                    continue
                assert field_name in item.fields
                before = application.snapshot(diagram).to_dict()
                application.execute(
                    diagram,
                    cast(str, contract["update_command"]),
                    {
                        "id": cast(str, item.fields["id"]),
                        "kind": kind,
                        "changes": {field_name: _argument(item.fields[field_name])},
                    },
                )
                assert application.snapshot(diagram).to_dict() == before, (
                    f"{diagram_id} {kind}.{field_name} changed after a no-op update"
                )

    contracts = _mapping(matrix["elements"])
    for item in elements:
        assert item.parent_id is not None
        assert item.position is not None
        placement = _mapping(_mapping(contracts[item.kind])["placement"])
        before = application.snapshot(diagram).to_dict()
        application.execute(
            diagram,
            cast(str, placement["move_command"]),
            {
                "id": cast(str, item.fields["id"]),
                "kind": item.kind,
                "parent_id": item.parent_id,
                "position": item.position,
            },
        )
        assert application.snapshot(diagram).to_dict() == before

    owners = {cast(str, item.fields["id"]): item.kind for item in elements}
    root_operation = cast(str, _mapping(matrix["root_collection"])["reorder_command"])
    for collection in collections:
        if collection.parent_id:
            owner = owners[collection.parent_id]
            operation = cast(str, _mapping(_mapping(contracts[owner])["child_collection"])["reorder_command"])
        else:
            operation = root_operation
        before = application.snapshot(diagram).to_dict()
        application.execute(
            diagram,
            operation,
            {"parent_id": collection.parent_id, "element_ids": list(collection.element_ids)},
        )
        assert application.snapshot(diagram).to_dict() == before

    conformed = application.snapshot(diagram).to_dict()
    restored = application.restore(_mapping(json.loads(json.dumps(conformed))))
    assert application.snapshot(restored).to_dict() == conformed
    assert application.render(restored) == application.render(diagram)


def _elements(
    value: object,
    kinds: Mapping[str, str],
    parent_id: str,
) -> tuple[tuple[MutationObject, ...], tuple[ElementCollection, ...]]:
    objects: list[MutationObject] = []
    collections: list[ElementCollection] = []
    items = _sequence(value)
    collections.append(
        ElementCollection(
            parent_id,
            tuple(cast(str, _mapping(_mapping(item)["fields"])["id"]) for item in items),
        )
    )
    for position, value in enumerate(items):
        item = _mapping(value)
        fields = _mapping(item["fields"])
        object_id = cast(str, fields["id"])
        objects.append(MutationObject(_kind(item, kinds), fields, parent_id, position))
        children = fields.get("elements")
        if children is not None:
            child_objects, child_collections = _elements(children, kinds, object_id)
            objects.extend(child_objects)
            collections.extend(child_collections)
    return tuple(objects), tuple(collections)


def _objects(value: object, kinds: Mapping[str, str]) -> tuple[MutationObject, ...]:
    return tuple(
        MutationObject(_kind(item, kinds), _mapping(item["fields"]))
        for value in _sequence(value)
        for item in (_mapping(value),)
    )


def _snapshot_kinds(catalogued: Mapping[str, Mapping[str, object]]) -> Mapping[str, str]:
    return {cast(str, schema["title"]): kind for kind, schema in catalogued.items()}


def _kind(item: Mapping[str, object], kinds: Mapping[str, str]) -> str:
    type_name = cast(str, item["$type"]).rsplit(":", maxsplit=1)[1]
    return kinds[type_name]


def _argument(value: object) -> object:
    if isinstance(value, list):
        return [_argument(item) for item in cast(list[object], value)]
    if not isinstance(value, dict):
        return value
    item = cast(dict[str, object], value)
    if "$enum" in item:
        return item["value"]
    if "$type" in item:
        return {name: _argument(field) for name, field in _mapping(item["fields"]).items()}
    return {name: _argument(field) for name, field in item.items()}


def _json(path: Path) -> Mapping[str, object]:
    return _mapping(json.loads(path.read_text(encoding="utf-8")))


def _mapping(value: object) -> Mapping[str, object]:
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _sequence(value: object) -> Sequence[object]:
    assert isinstance(value, list)
    return cast(list[object], value)
