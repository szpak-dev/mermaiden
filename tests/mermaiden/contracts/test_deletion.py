from typing import Any, cast

import pytest

from mermaiden import Application


class TestDeletion:
    def test_rejects_an_unsafe_delete_without_changing_the_diagram(self) -> None:
        application, diagram = self._sequence_diagram_with_dependants()
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"still has dependants; use cascade=True"):
            application.execute(diagram, "remove_element", {"id": "group_example"})
        assert application.snapshot(diagram).to_dict() == before

    def test_cascade_reports_every_removed_object_and_commits_atomically(self) -> None:
        application, diagram = self._sequence_diagram_with_dependants()
        report = application.execute(diagram, "remove_element", {"id": "group_example", "cascade": True})
        assert report is not None
        assert report.accepted
        assert tuple((item.kind, item.id) for item in report.removed) == (
            ("element", "group_example"),
            ("element", "participant_example"),
            ("relation", "message_example"),
            ("annotation", "note_example"),
        )
        snapshot = application.snapshot(diagram).to_dict()
        assert snapshot["relations"] == []
        assert snapshot["annotations"] == []
        assert application.render(diagram).endswith(
            'sequenceDiagram\nparticipant peer_example@{ "type": "participant" } as Peer\n'
        )

    def test_removes_relations_and_annotations_through_discovered_commands(self) -> None:
        application, diagram = self._sequence_diagram_with_dependants()
        annotation_report = application.execute(diagram, "remove_annotation", {"id": "note_example"})
        relation_report = application.execute(diagram, "remove_relation", {"id": "message_example"})
        assert annotation_report is not None
        assert tuple((item.kind, item.id) for item in annotation_report.removed) == (("annotation", "note_example"),)
        assert relation_report is not None
        assert tuple((item.kind, item.id) for item in relation_report.removed) == (("relation", "message_example"),)

    def test_requires_explicit_cascade_to_remove_a_relation_annotation(self) -> None:
        application, diagram = self._sequence_diagram_with_dependants()
        payload = application.snapshot(diagram).to_dict()
        annotation = cast(list[dict[str, Any]], payload["annotations"])[0]
        fields = cast(dict[str, Any], annotation["fields"])
        target = cast(list[dict[str, Any]], fields["targets"])[0]
        target_fields = cast(dict[str, Any], target["fields"])
        target_fields["id"] = "message_example"
        cast(dict[str, Any], target_fields["kind"])["value"] = "relation"
        restored = application.restore(payload)
        before = application.snapshot(restored).to_dict()
        with pytest.raises(RuntimeError, match=r"still has annotations"):
            application.execute(restored, "remove_relation", {"id": "message_example"})
        assert application.snapshot(restored).to_dict() == before
        report = application.execute(restored, "remove_relation", {"id": "message_example", "cascade": True})
        assert report is not None
        assert tuple((item.kind, item.id) for item in report.removed) == (
            ("relation", "message_example"),
            ("annotation", "note_example"),
        )

    @staticmethod
    def _sequence_diagram_with_dependants():
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        for command in (
            ("add_box", {"id": "group_example", "label": "Group"}),
            ("add_participant", {"id": "participant_example", "label": "Participant", "box_id": "group_example"}),
            ("add_participant", {"id": "peer_example", "label": "Peer"}),
            (
                "add_message",
                {
                    "id": "message_example",
                    "source_id": "participant_example",
                    "target_id": "peer_example",
                    "label": "Message",
                },
            ),
            ("add_note", {"id": "note_example", "text": "Note", "participant_ids": ["participant_example"]}),
        ):
            application.execute(diagram, *command)
        return (application, diagram)

    @pytest.mark.parametrize("cascade", ("true", "false", 0, 1, 0.5, None))
    @pytest.mark.parametrize(
        "operation,identifier", (("remove_element", "group_example"), ("remove_relation", "message_example"))
    )
    def test_non_boolean_cascade_is_rejected_before_deleting_anything(
        self, cascade: object, operation: str, identifier: str
    ) -> None:
        application, diagram = self._sequence_diagram_with_dependants()
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        with pytest.raises(RuntimeError, match=r"cascade"):
            application.execute(diagram, operation, {"id": identifier, "cascade": cascade})
        assert application.snapshot(diagram).to_dict() == before
        assert application.render(diagram) == source
