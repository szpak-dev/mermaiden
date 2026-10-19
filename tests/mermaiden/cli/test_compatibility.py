import pytest

from mermaiden import Application
from mermaiden.cli import MermaidenCli
from tests.fixtures.catalog import FixtureCatalog


def test_application_validates_every_registered_diagram_against_pinned_mermaid_schema() -> None:
    with Application.create() as application, MermaidenCli.create() as cli:
        report = cli.compatibility_report()
        expected = tuple(
            (info.id, info.config_key, info.schema_definition) for info in application.available_diagrams()
        )
        upstream = {item.config_key: item for item in cli.mermaid_diagram_configs()}
        mermaid_version = application.mermaid_version

    assert report.lock.mermaid_version == mermaid_version
    assert report.valid
    assert not report.missing_diagrams
    assert tuple((item.diagram_id, item.config_key, item.schema_definition) for item in report.diagrams) == expected
    configurations = {item.diagram_id: item.configuration.values for item in report.diagrams}
    assert all(values["wrap"] is True for values in configurations.values())
    assert all(item.config_key in configurations[item.diagram_id] for item in report.diagrams)
    assert configurations["architecture-beta"]["architecture"]["randomize"] is False
    assert configurations["architecture-beta"]["architecture"]["nodeSeparation"] == 75
    assert configurations["C4Context"]["c4"]["c4ShapeInRow"] == 4
    assert configurations["swimlane-beta"]["swimlane"]["lineHops"] == "arc"
    assert configurations["swimlane-beta"]["swimlane"]["automaticLaneOrdering"] is False
    assert configurations["stateDiagram-v2"]["state"]["defaultRenderer"] == "dagre-wrapper"
    assert configurations["requirementDiagram"]["requirement"]["useMaxWidth"] is True
    assert configurations["mindmap"]["mindmap"]["layoutAlgorithm"] == "cose-bilkent"
    assert configurations["pie"]["pie"]["donutHole"] == 0
    assert configurations["block"]["block"]["padding"] == 8
    assert "useWidth" not in configurations["block"]["block"]
    assert configurations["erDiagram"]["er"]["useMaxWidth"] is True
    assert configurations["gantt"]["gantt"]["weekday"] == "sunday"
    assert configurations["gantt"]["gantt"]["displayMode"] == ""
    assert configurations["gitGraph"]["gitGraph"]["mainBranchName"] == "main"
    assert configurations["ishikawa-beta"]["ishikawa"]["useMaxWidth"] is False
    assert configurations["journey"]["journey"]["actorColours"][0] == "#8FBC8F"
    assert configurations["packet"]["packet"]["bitsPerRow"] == 32
    assert configurations["radar-beta"]["radar"]["curveTension"] == 0.17
    assert configurations["sankey"]["sankey"]["useMaxWidth"] is False
    assert "nodeColors" not in configurations["sankey"]["sankey"]
    assert configurations["treeView-beta"]["treeView"]["filenameIcons"] == {}
    assert configurations["venn-beta"]["venn"]["useDebugLayout"] is False
    assert all(
        item.configuration.schema_definition == upstream[item.configuration.config_key].schema_definition
        for item in report.diagrams
    )


@pytest.mark.integration
def test_application_validates_populated_compatibility_fixtures_with_one_parser_run() -> None:
    with Application.create() as application, MermaidenCli.create() as cli:
        report = cli.verify_compatibility(FixtureCatalog(application).render())

    assert report.valid
    assert not report.syntax_violations


def test_application_lists_diagram_configs_from_mermaid_schema() -> None:
    with MermaidenCli.create() as cli:
        configs = cli.mermaid_diagram_configs()

    mindmap = next(item for item in configs if item.config_key == "mindmap")
    assert mindmap.schema_definition == "MindmapDiagramConfig"
    assert mindmap.schema["type"] == "object"
