import json

import pytest

from mermaiden import Application


class TestDraftPersistence:
    def test_constructs_a_flowchart_across_durable_draft_boundaries(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        empty = application.snapshot(diagram).to_dict()
        assert empty["draft"] is True
        diagram = application.restore(json.loads(json.dumps(empty)))
        assert application.snapshot(diagram).to_dict() == empty
        application.execute(diagram, "add_start", {"id": "start_example", "label": "Start"})
        intermediate = application.snapshot(diagram).to_dict()
        assert intermediate["draft"] is True
        diagram = application.restore(json.loads(json.dumps(intermediate)))
        assert application.snapshot(diagram).to_dict() == intermediate
        with pytest.raises(RuntimeError, match=r"Cannot render invalid diagram 'flowchart'"):
            application.render(diagram)
        before_rejection = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_flow",
                {"id": "invalid_example", "source_id": "start_example", "target_id": "missing_example"},
            )
        assert application.snapshot(diagram).to_dict() == before_rejection
        application.execute(diagram, "add_end", {"id": "end_example", "label": "End"})
        diagram = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        application.execute(
            diagram, "add_flow", {"id": "path_example", "source_id": "start_example", "target_id": "end_example"}
        )
        diagram = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert application.snapshot(diagram).to_dict()["draft"] is False
        assert application.render(diagram).endswith(
            'flowchart TD\ne_v_start_example@{ shape: circle, label: "Start" }\n'
            'e_v_end_example@{ shape: dbl-circ, label: "End" }\n'
            "e_v_start_example r_v_path_example@--> e_v_end_example\n"
        )
