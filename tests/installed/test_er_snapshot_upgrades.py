from copy import deepcopy

import pytest

from mermaiden import Application, SnapshotUpgradeError
from tests.fixtures.snapshot_upgrades import SnapshotExamples

pytestmark = pytest.mark.installed


class ErSnapshotExamples:
    def payload(self, application: Application, source: str, key: str) -> dict[str, object]:
        examples = SnapshotExamples()
        if source == "13.1.0":
            bundle = examples.load("upgrade-13.1.0-er.json")
            cases = examples.mapping(bundle["cases"])
            return examples.mapping(examples.mapping(cases[key])["snapshot"])
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "example_entity", "label": "EXAMPLE"})
        application.execute(
            diagram,
            "add_attribute",
            {
                "id": "example_attribute",
                "entity_id": "example_entity",
                "label": "example_id",
                "data_type": "string",
                "keys": [] if key == "none" else [key],
                "comment": "Example attribute",
            },
        )
        return application.snapshot(diagram).to_dict()

    def attribute(self, payload: dict[str, object]) -> dict[str, object]:
        examples = SnapshotExamples()
        entity = examples.objects(payload["elements"])[0]
        return examples.objects(examples.mapping(entity["fields"])["elements"])[0]

    def replaced(self, payload: dict[str, object], attribute: dict[str, object]) -> dict[str, object]:
        examples = SnapshotExamples()
        entity = examples.objects(payload["elements"])[0]
        fields = examples.mapping(entity["fields"])
        return {**payload, "elements": [{**entity, "fields": {**fields, "elements": [attribute]}}]}


@pytest.mark.parametrize("source", ("current", "13.1.0"))
@pytest.mark.parametrize("allow_loss", (False, True))
@pytest.mark.parametrize(
    "field,value",
    (
        ("data_type", "string\ninjected"),
        ("data_type", 1),
        ("keys", ["PK\ninjected"]),
        ("keys", [1]),
        ("keys", None),
        ("comment", False),
        ("example_unknown", "example"),
    ),
)
def test_rejects_invalid_er_attribute_values_without_changing_input(
    source: str, allow_loss: bool, field: str, value: object
) -> None:
    examples = ErSnapshotExamples()
    with Application.create() as application:
        payload = examples.payload(application, source, "PK")
        attribute = examples.attribute(payload)
        fields = SnapshotExamples().mapping(attribute["fields"])
        payload = examples.replaced(payload, {**attribute, "fields": {**fields, field: value}})
        before = deepcopy(payload)
        with pytest.raises(SnapshotUpgradeError) as failure:
            application.upgrade_snapshot(payload, allow_loss=allow_loss)
        assert failure.value.paths
        assert payload == before


@pytest.mark.parametrize("source", ("current", "13.1.0"))
@pytest.mark.parametrize("attack", ("missing_type", "missing_field", "unknown_type", "extra_encoded_field"))
def test_rejects_incomplete_or_unsupported_er_attributes_even_with_loss_permission(source: str, attack: str) -> None:
    examples = ErSnapshotExamples()
    with Application.create() as application:
        payload = examples.payload(application, source, "PK")
        attribute = examples.attribute(payload)
        if attack == "missing_type":
            del attribute["$type"]
        if attack == "missing_field":
            fields = SnapshotExamples().mapping(attribute["fields"])
            del fields["keys"]
            attribute["fields"] = fields
        if attack == "unknown_type":
            attribute["$type"] = "mermaiden/element/erDiagram/example_unknown"
        if attack == "extra_encoded_field":
            attribute["example_unknown"] = True
        payload = examples.replaced(payload, attribute)
        before = deepcopy(payload)
        with pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)
        assert payload == before


@pytest.mark.parametrize("field,value", (("min_entity_width", True), ("use_max_width", 1)))
def test_rejects_boolean_number_coercion_in_er_configuration(field: str, value: object) -> None:
    with Application.create() as application:
        payload = ErSnapshotExamples().payload(application, "current", "PK")
        payload = SnapshotExamples().configured(payload, {field: value})
        before = deepcopy(payload)
        with pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)
        assert payload == before


@pytest.mark.parametrize("source", ("current", "13.1.0"))
@pytest.mark.parametrize("key", ("none", "PK", "FK", "UK"))
def test_preserves_er_attributes_keys_and_caller_input_through_upgrade(source: str, key: str) -> None:
    examples = ErSnapshotExamples()
    with Application.create() as application:
        payload = examples.payload(application, source, key)
        before = deepcopy(payload)
        result = application.upgrade_snapshot(payload)
        upgraded = result.snapshot.to_dict()
        assert upgraded["elements"] == before["elements"]
        assert upgraded["relations"] == before["relations"]
        assert upgraded["properties"] == before["properties"]
        assert not any(change.requires_loss_acceptance for change in result.changes)
        if source == "current":
            assert upgraded == before
            assert result.changes == ()
        else:
            assert result.changes
            assert upgraded["version"] == application.snapshot_contract_identity("erDiagram").snapshot_version
        restored = application.restore(upgraded)
        assert application.snapshot(restored).to_dict() == upgraded
        key_text = "" if key == "none" else f" {key}"
        assert f'string example_id{key_text} "Example attribute"' in application.render(restored)
        assert application.upgrade_snapshot(upgraded).changes == ()
        assert payload == before
        payload["elements"] = []
        assert result.snapshot.to_dict() == upgraded


def test_recovers_after_rejecting_an_er_snapshot() -> None:
    with Application.create() as application:
        payload = ErSnapshotExamples().payload(application, "current", "FK")
        with pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot({**payload, "example_unknown": True})
        result = application.upgrade_snapshot(payload)
        restored = application.restore(result.snapshot.to_dict())
        assert 'string example_id FK "Example attribute"' in application.render(restored)
