from copy import deepcopy

import pytest

from mermaiden import Application, SnapshotUpgradeError
from tests.fixtures.snapshot_upgrades import SnapshotExamples


class TestHistoricalSnapshotAttacks:
    def test_reports_unknown_historical_fields_as_escaped_json_pointers(self) -> None:
        examples = SnapshotExamples()
        payload = examples.configured(examples.load("upgrade-v7-class.json"), {"example/~field": 1})
        with Application.create() as application, pytest.raises(SnapshotUpgradeError) as failure:
            application.upgrade_snapshot(payload)
        assert failure.value.paths == ("/configuration/fields/example~1~0field",)

    @pytest.mark.parametrize(
        "kind,field,value",
        (
            ("packet", "title", "Title example\ninjected"),
            ("packet", "title", " Title example "),
            ("gantt", "date_format", "YYYY-MM-DD\ninjected"),
            ("gantt", "date_format", ""),
        ),
    )
    def test_rejects_incompatible_persisted_titles_and_date_formats(self, kind: str, field: str, value: str) -> None:
        with Application.create() as application:
            payload = application.snapshot(application.create_diagram(kind)).to_dict()
            payload["version"] = 11
            payload["properties"] = {**SnapshotExamples().mapping(payload["properties"]), field: value}
            before = deepcopy(payload)
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload, allow_loss=True)
            assert failure.value.paths == (f"/properties/{field}",)
            assert payload == before

    @pytest.mark.parametrize("version", (6, 7))
    @pytest.mark.parametrize("attack", ("missing", "extra", "wrong_type"))
    def test_rejects_invalid_original_configuration_before_introducing_fields(self, version: int, attack: str) -> None:
        examples = SnapshotExamples()
        payload = examples.load("upgrade-v6-class.json")
        payload["version"] = version
        configuration = examples.mapping(payload["configuration"])
        fields = examples.mapping(configuration["fields"])
        if attack == "missing":
            del fields["wrap"]
        if attack == "extra":
            fields["html_labels"] = False
        if attack == "wrong_type":
            fields["wrap"] = "true"
        payload["configuration"] = {**configuration, "fields": fields}
        before = deepcopy(payload)
        with Application.create() as application, pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)
        assert payload == before

    def test_rejects_multiple_generic_arguments_in_v6(self) -> None:
        payload = SnapshotExamples().load("upgrade-v7-class.json")
        payload["version"] = 6
        with Application.create() as application, pytest.raises(SnapshotUpgradeError) as failure:
            application.upgrade_snapshot(payload)
        assert failure.value.paths == ("/elements/0",)

    @pytest.mark.parametrize("value", ("example_unknown", "dagre", True))
    def test_rejects_unsupported_legacy_renderer_choices(self, value: object) -> None:
        examples = SnapshotExamples()
        payload = examples.mapping(examples.load("upgrade-v8-renderers.json")["classDiagram"])
        payload = examples.configured(
            payload, {"default_renderer": {"$enum": "mermaiden/enum/classDiagram/class_renderer", "value": value}}
        )
        with Application.create() as application, pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)

    @pytest.mark.parametrize("value", (0, 1, "false", None))
    def test_rejects_invalid_retired_html_labels_before_discarding(self, value: object) -> None:
        examples = SnapshotExamples()
        payload = examples.configured(examples.load("upgrade-v10-class.json"), {"html_labels": value})
        with Application.create() as application, pytest.raises(SnapshotUpgradeError):
            application.upgrade_snapshot(payload, allow_loss=True)

    def test_requires_loss_permission_for_enabled_retired_html_labels(self) -> None:
        examples = SnapshotExamples()
        payload = examples.configured(examples.load("upgrade-v10-class.json"), {"html_labels": True})
        with Application.create() as application:
            with pytest.raises(SnapshotUpgradeError) as failure:
                application.upgrade_snapshot(payload)
            path = "/configuration/fields/html_labels"
            assert failure.value.paths == (path,)
            losses = tuple(change for change in failure.value.changes if change.requires_loss_acceptance)
            assert losses[0].discarded == {path: True}
            accepted = application.upgrade_snapshot(payload, allow_loss=True)
            assert accepted.changes == failure.value.changes


class TestHistoricalSnapshotPreservation:
    @pytest.mark.parametrize(
        "kind,field,value",
        (
            ("C4Context", "message_font_size", "18"),
            ("swimlane-beta", "line_hops", False),
            ("packet", "bits_per_row", 16.0),
        ),
    )
    def test_preserves_explicit_values_when_upgrading_historical_configuration_wrappers(
        self, kind: str, field: str, value: object
    ) -> None:
        examples = SnapshotExamples()
        payload = examples.mapping(examples.load("upgrade-v7-empty.json")[kind])
        payload = examples.configured(payload, {field: value})
        with Application.create() as application:
            result = application.upgrade_snapshot(payload)
            current = examples.mapping(result.snapshot.configuration["fields"])
            if kind == "packet":
                assert current[field] == 16
            else:
                wrapper = examples.mapping(current[field])
                assert examples.mapping(wrapper["fields"])["root"] == value
            assert (
                application.snapshot(application.restore(result.snapshot.to_dict())).to_dict()
                == result.snapshot.to_dict()
            )

    @pytest.mark.parametrize(
        "fixture",
        (
            "upgrade-v6-class.json",
            "upgrade-v7-class.json",
            "upgrade-v10-class.json",
            "upgrade-v11-packet.json",
            "upgrade-v11-flowchart.json",
        ),
    )
    def test_historical_snapshots_upgrade_deterministically_and_restore(self, fixture: str) -> None:
        examples = SnapshotExamples()
        payload = examples.load(fixture)
        before = deepcopy(payload)
        with Application.create() as application:
            result = application.upgrade_snapshot(payload)
            assert result == application.upgrade_snapshot(payload)
            upgraded = result.snapshot.to_dict()
            assert upgraded["version"] == 12
            assert upgraded["relations"] == before["relations"]
            assert upgraded["properties"] == before["properties"]
            if payload["kind"] != "packet":
                assert upgraded["elements"] == before["elements"]
            restored = application.restore(upgraded)
            assert application.snapshot(restored).to_dict() == upgraded
            assert application.render(restored)
            assert not any(change.requires_loss_acceptance for change in result.changes)
            assert payload == before

    @pytest.mark.parametrize("version", (6, 7))
    def test_upgrades_configuration_for_every_historical_diagram_kind(self, version: int) -> None:
        examples = SnapshotExamples()
        snapshots = examples.load("upgrade-v7-empty.json")
        with Application.create() as application:
            for kind, value in snapshots.items():
                payload = {**examples.mapping(value), "version": version}
                before = deepcopy(payload)
                result = application.upgrade_snapshot(payload)
                upgraded = result.snapshot.to_dict()
                assert upgraded["kind"] == kind
                assert application.snapshot(application.restore(upgraded)).to_dict() == upgraded, kind
                assert not any(change.requires_loss_acceptance for change in result.changes), kind
                assert payload == before

    @pytest.mark.parametrize("kind", ("classDiagram", "flowchart", "stateDiagram-v2"))
    @pytest.mark.parametrize("renderer,layout", (("elk", "elk"), ("dagre-wrapper", "dagre")))
    def test_translates_explicit_renderer_selection_to_equivalent_layout(
        self, kind: str, renderer: str, layout: str
    ) -> None:
        examples = SnapshotExamples()
        payload = examples.mapping(examples.load("upgrade-v8-renderers.json")[kind])
        configuration = examples.mapping(payload["configuration"])
        fields = examples.mapping(configuration["fields"])
        value = examples.mapping(fields["default_renderer"])
        payload = examples.configured(payload, {"default_renderer": {**value, "value": renderer}})
        with Application.create() as application:
            result = application.upgrade_snapshot(payload)
            current = examples.mapping(result.snapshot.configuration["fields"])
            assert "default_renderer" not in current
            assert current["layout"] == {
                "$type": f"mermaiden/value/{kind}/omittable_layout",
                "fields": {"root": layout},
            }
            assert any("/configuration/fields/default_renderer" in change.paths for change in result.changes)

    def test_preserves_explicit_v10_layout_while_reporting_html_label_retirement(self) -> None:
        examples = SnapshotExamples()
        payload = examples.load("upgrade-v10-class.json")
        with Application.create() as application:
            result = application.upgrade_snapshot(payload)
            current = examples.mapping(result.snapshot.configuration["fields"])
            assert current["layout"] == {
                "$type": "mermaiden/value/classDiagram/omittable_layout",
                "fields": {"root": "dagre"},
            }
            assert "html_labels" not in current
            retired = tuple(change for change in result.changes if "/configuration/fields/html_labels" in change.paths)
            assert retired[0].discarded == {"/configuration/fields/html_labels": False}
            assert not retired[0].requires_loss_acceptance

    def test_introduces_explicit_flowchart_step_values(self) -> None:
        payload = SnapshotExamples().load("upgrade-v11-flowchart.json")
        with Application.create() as application:
            result = application.upgrade_snapshot(payload)
            current = SnapshotExamples().mapping(result.snapshot.configuration["fields"])
            assert current["step_duration"] == 1
            assert current["step_numbers"] is False
            paths = {path for change in result.changes for path in change.paths}
            assert {"/configuration/fields/step_duration", "/configuration/fields/step_numbers"} <= paths
