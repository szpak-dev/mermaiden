from copy import deepcopy

import pytest

from mermaiden import Application, ApplicationClosed, SnapshotError, SnapshotUpgradeError
from tests.fixtures.snapshot_upgrades import SnapshotExamples


class TestSnapshotUpgradeAttacks:
    def test_reports_unknown_envelope_keys_as_escaped_json_pointers(self) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("block")).to_dict()
            payload["example/~field"] = 1
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload)
            assert failure.value.paths == ("/example~1~0field",)

    @pytest.mark.parametrize("field,value", (("visibility", "public"), ("type", {"name": "Example", "arguments": []})))
    def test_rejects_missing_nested_type_markers(self, field: str, value: object) -> None:
        examples = SnapshotExamples()
        payload = examples.load("upgrade-v7-class.json")
        elements = examples.objects(payload["elements"])
        fields = examples.mapping(elements[0]["fields"])
        attributes = examples.objects(fields["attributes"])
        attributes[0]["fields"] = {**examples.mapping(attributes[0]["fields"]), field: value}
        fields["attributes"] = attributes
        elements[0]["fields"] = fields
        payload["elements"] = elements
        with Application.create() as application, pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload)

    @pytest.mark.parametrize("version", (0, 5, 13, -1, True, 11.0, "11", None))
    def test_rejects_invalid_or_unsupported_versions_without_mutation(self, version: object) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("block")).to_dict()
            payload["version"] = version
            before = deepcopy(payload)
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload)
            assert failure.value.paths
            assert payload == before

    @pytest.mark.parametrize(
        "field", ("version", "kind", "draft", "configuration", "elements", "relations", "annotations", "properties")
    )
    def test_rejects_missing_envelope_fields(self, field: str) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("block")).to_dict()
            del payload[field]
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload)
            assert failure.value.paths == (f"/{field}",)

    @pytest.mark.parametrize(
        "changes",
        ({"example_extra": True}, {"kind": "example_unknown"}, {"draft": 1}, {"elements": {}}, {"configuration": []}),
    )
    def test_rejects_malformed_envelope_values(self, changes: dict[str, object]) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("block")).to_dict()
            with pytest.raises(SnapshotUpgradeError):
                application.upgrade_snapshot({**payload, **changes})

    @pytest.mark.parametrize(
        "field,value",
        (
            ("bits_per_row", "32"),
            ("bits_per_row", True),
            ("bits_per_row", 1.5),
            ("show_bits", 1),
            ("row_height", "32"),
            ("example_extra", 1),
        ),
    )
    def test_rejects_coercion_and_unknown_configuration_even_with_loss_permission(
        self, field: str, value: object
    ) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("packet")).to_dict()
            payload = SnapshotExamples().configured(payload, {field: value})
            before = deepcopy(payload)
            with pytest.raises(SnapshotUpgradeError):
                application.upgrade_snapshot(payload, allow_loss=True)
            assert payload == before

    @pytest.mark.parametrize(
        "coordinates",
        (
            {"start": None, "end": None, "bits": None},
            {"start": 0, "end": 7, "bits": 8},
            {"start": None, "end": 7, "bits": None},
            {"start": -1, "end": 7, "bits": None},
            {"start": 8, "end": 7, "bits": None},
            {"start": None, "end": None, "bits": 0},
            {"start": None, "end": None, "bits": -1},
            {"start": True, "end": None, "bits": None},
            {"start": "0", "end": 7, "bits": None},
            {"start": None, "end": None, "bits": 1.0},
            {"start": 0, "end": None},
            {"start": 0, "end": None, "bits": None, "example_extra": 1},
        ),
    )
    def test_rejects_ambiguous_invalid_or_incomplete_packet_modes(self, coordinates: dict[str, object]) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("packet")).to_dict()
            payload = SnapshotExamples().packet(payload, coordinates)
            before = deepcopy(payload)
            with pytest.raises(SnapshotUpgradeError):
                application.upgrade_snapshot(payload, allow_loss=True)
            assert payload == before

    @pytest.mark.parametrize("fixture", ("class-note-v9.json", "tree-annotation-v9.json"))
    def test_requires_explicit_loss_permission_and_reports_complete_original_annotations(self, fixture: str) -> None:
        with Application.create() as application:
            payload = SnapshotExamples().load(fixture)
            before = deepcopy(payload)
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload)
            assert failure.value.paths == ("/annotations/0",)
            losses = tuple(change for change in failure.value.changes if change.requires_loss_acceptance)
            assert len(losses) == 1
            assert losses[0].discarded == {"/annotations/0": SnapshotExamples().objects(payload["annotations"])[0]}
            assert payload == before

    @pytest.mark.parametrize("fixture", ("class-note-v9.json", "tree-annotation-v9.json"))
    @pytest.mark.parametrize(
        "attack", ("missing_target", "wrong_target_kind", "extra_field", "missing_field", "duplicate_id", "wrong_type")
    )
    def test_loss_permission_cannot_hide_invalid_removed_annotations(self, fixture: str, attack: str) -> None:
        examples = SnapshotExamples()
        payload = examples.load(fixture)
        annotations = examples.objects(payload["annotations"])
        fields = examples.mapping(annotations[0]["fields"])
        targets = examples.objects(fields["targets"])
        target = examples.mapping(targets[0]["fields"])
        if attack == "missing_target":
            target["id"] = "missing_example"
        if attack == "wrong_target_kind":
            target["kind"] = {**examples.mapping(target["kind"]), "value": "relation"}
        if attack == "extra_field":
            fields["example_extra"] = "example"
        if attack == "missing_field":
            del fields["id"]
        if attack == "wrong_type":
            annotations[0]["$type"] = "mermaiden/annotation/example/unknown"
        targets[0]["fields"] = target
        fields["targets"] = targets
        annotations[0]["fields"] = fields
        if attack == "duplicate_id":
            annotations.append(deepcopy(annotations[0]))
        payload["annotations"] = annotations
        before = deepcopy(payload)
        with Application.create() as application, pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)
        assert payload == before

    def test_closed_application_rejects_upgrade(self) -> None:
        application = Application.create()
        payload = application.snapshot(application.create_diagram("block")).to_dict()
        application.close()
        with pytest.raises(ApplicationClosed):
            application.upgrade_snapshot(payload)


class TestSnapshotUpgradePreservation:
    def test_preserves_supported_annotations_on_other_diagram_kinds(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("sequenceDiagram")
            application.execute(
                diagram, "add_participant", {"id": "participant_example", "label": "Participant example"}
            )
            application.execute(
                diagram,
                "add_note",
                {"id": "note_example", "text": "Note example", "participant_ids": ["participant_example"]},
            )
            payload = application.snapshot(diagram).to_dict()
            payload["version"] = 9
            result = application.upgrade_snapshot(payload)
            assert result.snapshot.to_dict()["annotations"] == payload["annotations"]
            assert not any(change.requires_loss_acceptance for change in result.changes)
            assert application.render(application.restore(result.snapshot.to_dict()))

    def test_preserves_explicit_draft_status_on_otherwise_valid_current_content(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class example"})
            payload = application.snapshot(diagram).to_dict()
            payload["draft"] = True
            result = application.upgrade_snapshot(payload)
            assert result.snapshot.to_dict() == payload
            assert result.changes == ()

    def test_current_snapshots_of_every_kind_are_unchanged_and_detached(self) -> None:
        with Application.create() as application:
            for info in application.available_diagrams():
                payload = application.snapshot(application.create_diagram(info.id)).to_dict()
                before = deepcopy(payload)
                result = application.upgrade_snapshot(payload)
                assert result.changes == (), info.id
                assert result.snapshot.to_dict() == before, info.id
                assert application.snapshot(application.restore(result.snapshot.to_dict())).to_dict() == before
                payload["configuration"] = {}
                assert result.snapshot.to_dict() == before

    @pytest.mark.parametrize("fixture", ("class-note-v9.json", "tree-annotation-v9.json"))
    def test_preserves_elements_relationships_configuration_and_original_loss_provenance(self, fixture: str) -> None:
        with Application.create() as application:
            payload = SnapshotExamples().load(fixture)
            before = deepcopy(payload)
            first = application.upgrade_snapshot(payload, allow_loss=True)
            second = application.upgrade_snapshot(payload, allow_loss=True)
            upgraded = first.snapshot.to_dict()
            assert first == second
            assert upgraded["elements"] == payload["elements"]
            assert upgraded["relations"] == payload["relations"]
            assert upgraded["annotations"] == []
            assert payload == before
            assert application.snapshot(application.restore(upgraded)).to_dict() == upgraded
            assert application.upgrade_snapshot(upgraded).changes == ()
            with pytest.raises(SnapshotError):
                application.restore(payload)

    @pytest.mark.parametrize(
        "coordinates,expected",
        (
            ({"start": 0, "end": None, "bits": None}, '0: "Field example"'),
            ({"start": 0, "end": 7, "bits": None}, '0-7: "Field example"'),
            ({"start": None, "end": None, "bits": 8}, '+8: "Field example"'),
        ),
    )
    def test_restores_exact_legacy_packet_position_semantics(
        self, coordinates: dict[str, object], expected: str
    ) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram("packet")).to_dict()
            payload = SnapshotExamples().packet(payload, coordinates)
            before = deepcopy(payload)
            result = application.upgrade_snapshot(payload)
            assert application.render(application.restore(result.snapshot.to_dict())).endswith(expected + "\n")
            assert payload == before
            assert any(change.paths == ("/elements/0",) for change in result.changes)
            assert not any(change.requires_loss_acceptance for change in result.changes)

    def test_recovers_after_a_rejected_upgrade(self) -> None:
        with Application.create() as application:
            payload = SnapshotExamples().load("class-note-v9.json")
            with pytest.raises(SnapshotUpgradeError):
                application.upgrade_snapshot(payload)
            result = application.upgrade_snapshot(payload, allow_loss=True)
            restored = application.restore(result.snapshot.to_dict())
            application.execute(restored, "add_class", {"id": "recovered_example", "label": "Recovered example"})
            assert "Recovered example" in application.render(restored)
