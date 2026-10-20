import pytest
from pydantic import RootModel

from mermaiden import Application
from mermaiden.cli import MermaidenCli
from tests.fixtures.catalog import FixtureCatalog


class ObjectMapping(RootModel[dict[str, object]]):
    pass


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
    architecture = ObjectMapping.model_validate(configurations["architecture-beta"]["architecture"]).root
    c4 = ObjectMapping.model_validate(configurations["C4Context"]["c4"]).root
    swimlane = ObjectMapping.model_validate(configurations["swimlane-beta"]["swimlane"]).root
    state = ObjectMapping.model_validate(configurations["stateDiagram-v2"]["state"]).root
    requirement = ObjectMapping.model_validate(configurations["requirementDiagram"]["requirement"]).root
    mindmap = ObjectMapping.model_validate(configurations["mindmap"]["mindmap"]).root
    pie = ObjectMapping.model_validate(configurations["pie"]["pie"]).root
    block = ObjectMapping.model_validate(configurations["block"]["block"]).root
    er = ObjectMapping.model_validate(configurations["erDiagram"]["er"]).root
    gantt = ObjectMapping.model_validate(configurations["gantt"]["gantt"]).root
    git_graph = ObjectMapping.model_validate(configurations["gitGraph"]["gitGraph"]).root
    ishikawa = ObjectMapping.model_validate(configurations["ishikawa-beta"]["ishikawa"]).root
    journey = ObjectMapping.model_validate(configurations["journey"]["journey"]).root
    journey_colours = RootModel[list[str]].model_validate(journey["actorColours"]).root
    packet = ObjectMapping.model_validate(configurations["packet"]["packet"]).root
    radar = ObjectMapping.model_validate(configurations["radar-beta"]["radar"]).root
    sankey = ObjectMapping.model_validate(configurations["sankey"]["sankey"]).root
    tree_view = ObjectMapping.model_validate(configurations["treeView-beta"]["treeView"]).root
    venn = ObjectMapping.model_validate(configurations["venn-beta"]["venn"]).root
    assert all(values["wrap"] is True for values in configurations.values())
    assert all(item.config_key in configurations[item.diagram_id] for item in report.diagrams)
    assert architecture["randomize"] is False
    assert architecture["nodeSeparation"] == 75
    assert c4["c4ShapeInRow"] == 4
    assert swimlane["lineHops"] == "arc"
    assert swimlane["automaticLaneOrdering"] is False
    assert state["defaultRenderer"] == "dagre-wrapper"
    assert requirement["useMaxWidth"] is True
    assert mindmap["layoutAlgorithm"] == "cose-bilkent"
    assert pie["donutHole"] == 0
    assert block["padding"] == 8
    assert "useWidth" not in block
    assert er["useMaxWidth"] is True
    assert gantt["weekday"] == "sunday"
    assert gantt["displayMode"] == ""
    assert git_graph["mainBranchName"] == "main"
    assert ishikawa["useMaxWidth"] is False
    assert journey_colours[0] == "#8FBC8F"
    assert packet["bitsPerRow"] == 32
    assert radar["curveTension"] == 0.17
    assert sankey["useMaxWidth"] is False
    assert "nodeColors" not in sankey
    assert tree_view["filenameIcons"] == {}
    assert venn["useDebugLayout"] is False
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
