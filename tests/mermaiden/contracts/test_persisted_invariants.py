import json

import pytest

from mermaiden import Application


class TestPersistedInvariants:
    @pytest.mark.parametrize("kind", ("gantt", "journey", "packet", "pie", "radar-beta", "timeline"))
    @pytest.mark.parametrize("title", ("Title\nsection injected", "Title\x00", " Title", "Title "))
    def test_restore_rejects_titles_that_bypass_the_command_text_policy(self, kind: str, title: str) -> None:
        with Application.create() as application:
            diagram = application.create_diagram(kind)
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(RuntimeError, match="invalid arguments"):
                application.execute(diagram, "set_title", {"title": title})
            payload = json.loads(json.dumps(before))
            payload["properties"]["title"] = title
            with pytest.raises(RuntimeError, match="title"):
                application.restore(payload)
            assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.parametrize("kind", ("gantt", "journey", "packet", "pie", "radar-beta", "timeline"))
    @pytest.mark.parametrize("title", ("", 'Release: "Łódź" & <team> #1!'))
    def test_restore_preserves_unset_titles_and_readable_punctuation(self, kind: str, title: str) -> None:
        with Application.create() as application:
            diagram = application.create_diagram(kind)
            if title:
                application.execute(diagram, "set_title", {"title": title})
            payload = application.snapshot(diagram).to_dict()
            restored = application.restore(json.loads(json.dumps(payload)))
            assert application.snapshot(restored).to_dict() == payload

    def test_restore_rejects_a_date_format_that_injects_a_gantt_statement(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("gantt")
            application.execute(diagram, "add_marker", {"id": "today_example", "label": "Today", "date": "2026-08-02"})
            before = application.snapshot(diagram).to_dict()
            injected = "YYYY-MM-DD\nsection injected"
            with pytest.raises(RuntimeError, match="invalid arguments"):
                application.execute(diagram, "set_date_format", {"date_format": injected})
            payload = json.loads(json.dumps(before))
            payload["properties"]["date_format"] = injected
            with pytest.raises(RuntimeError, match="date_format"):
                application.restore(payload)
            application.execute(diagram, "set_date_format", {"date_format": "DD/MM/YYYY"})
            restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
            assert "dateFormat DD/MM/YYYY\n" in application.render(restored)

    @pytest.mark.parametrize("draft", (False, True))
    def test_restore_rejects_a_marker_nested_under_a_section_even_in_a_draft(self, draft: bool) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("gantt")
            application.execute(diagram, "add_section", {"id": "delivery_example", "label": "Delivery"})
            application.execute(diagram, "add_marker", {"id": "today_example", "label": "Today", "date": "2026-08-02"})
            before = application.snapshot(diagram).to_dict()
            payload = json.loads(json.dumps(before))
            section, marker = payload["elements"]
            section["fields"]["elements"] = [marker]
            payload["elements"] = [section]
            payload["draft"] = draft
            with pytest.raises(RuntimeError, match="cannot be placed"):
                application.restore(payload)
            assert application.snapshot(diagram).to_dict() == before
            restored = application.restore(json.loads(json.dumps(before)))
            assert application.render(restored) == application.render(diagram)

    def test_invalid_move_rolls_back_and_valid_move_still_succeeds(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("gantt")
            application.execute(diagram, "add_section", {"id": "delivery_example", "label": "Delivery"})
            application.execute(diagram, "add_section", {"id": "release_example", "label": "Release"})
            application.execute(diagram, "add_marker", {"id": "today_example", "label": "Today", "date": "2026-08-02"})
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(RuntimeError, match="cannot be placed"):
                application.execute(
                    diagram, "move_element", {"id": "today_example", "kind": "marker", "parent_id": "delivery_example"}
                )
            assert application.snapshot(diagram).to_dict() == before
            application.execute(
                diagram,
                "add_task",
                {
                    "id": "build_example",
                    "label": "Build",
                    "section_id": "delivery_example",
                    "start": {"kind": "date", "date": "2026-08-01"},
                    "finish": {"kind": "duration", "amount": 1},
                },
            )
            application.execute(
                diagram, "move_element", {"id": "build_example", "kind": "task", "parent_id": "release_example"}
            )
            assert "section Release\nBuild :" in application.render(diagram)
