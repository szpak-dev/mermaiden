import json

import pytest
from pydantic import RootModel

from mermaiden import Application


class JsonObject(RootModel[dict[str, object]]):
    pass


class TestClassLabels:
    @pytest.mark.parametrize("field", ("htmlLabels", "html_labels"))
    @pytest.mark.parametrize("value", (True, False))
    @pytest.mark.parametrize("batch", (False, True))
    def test_rejects_label_overrides_without_mutation_and_recovers(self, field: str, value: bool, batch: bool) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class example"})
            application.execute(diagram, "configure", {"padding": 9})
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            with pytest.raises(RuntimeError, match="'configure' has invalid arguments"):
                if batch:
                    application.apply_batch(
                        diagram,
                        [
                            {"operation": "add_class", "arguments": {"id": "pending_example", "label": "Example"}},
                            {"operation": "configure", "arguments": {field: value}},
                        ],
                    )
                else:
                    application.execute(diagram, "configure", {field: value})
            assert application.snapshot(diagram).to_dict() == before
            assert application.render(diagram) == source
            application.execute(diagram, "configure", {"padding": 12})
            assert '"padding": 12.0' in application.render(diagram)
            assert "\n  htmlLabels: false\n" in application.render(diagram)

    @pytest.mark.parametrize("value", (True, False))
    def test_rejects_obsolete_snapshot_configuration_without_rewriting_input(self, value: bool) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class example"})
            current = application.snapshot(diagram).to_dict()
            invalid = dict(current)
            configuration = JsonObject.model_validate(invalid["configuration"]).root
            fields = JsonObject.model_validate(configuration["fields"]).root
            fields["html_labels"] = value
            invalid["configuration"] = {**configuration, "fields": fields}
            before = json.dumps(invalid, sort_keys=True)
            with pytest.raises(RuntimeError, match="html_labels"):
                application.restore(invalid)
            assert json.dumps(invalid, sort_keys=True) == before
            assert application.snapshot(application.restore(current)).to_dict() == current

    @pytest.mark.parametrize("wrap", (True, False))
    def test_svg_label_policy_survives_configuration_and_restore(self, wrap: bool) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class example"})
            properties = JsonObject.model_validate(
                application.command_payload("classDiagram", "configure").schema()["properties"]
            ).root
            assert "htmlLabels" not in properties
            assert "html_labels" not in properties
            application.execute(diagram, "configure", {"wrap": wrap, "padding": 8})
            snapshot = application.snapshot(diagram).to_dict()
            configuration = JsonObject.model_validate(snapshot["configuration"]).root
            assert "html_labels" not in JsonObject.model_validate(configuration["fields"]).root
            assert snapshot["version"] == 12
            source = application.render(application.restore(snapshot))
            assert source == application.render(diagram)
            assert source.count("htmlLabels") == 1
            assert "\n  htmlLabels: false\n" in source
            assert f"\n  wrap: {str(wrap).lower()}\n" in source
            assert '"padding": 8.0' in source
