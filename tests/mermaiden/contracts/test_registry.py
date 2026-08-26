import pytest

from mermaiden.application import Application


def test_registry_lists_every_implemented_diagram_with_mermaid_metadata() -> None:
    diagrams = Application.create().available_diagrams()

    assert [(item.id, item.config_key, item.schema_definition) for item in diagrams] == [
        ("C4Context", "c4", "C4DiagramConfig"),
        ("architecture-beta", "architecture", "ArchitectureDiagramConfig"),
        ("block", "block", "BlockDiagramConfig"),
        ("classDiagram", "class", "ClassDiagramConfig"),
        ("cynefin-beta", "cynefin", "CynefinDiagramConfig"),
        ("erDiagram", "er", "ErDiagramConfig"),
        ("eventmodeling", "eventmodeling", "EventModelingDiagramConfig"),
        ("flowchart", "flowchart", "FlowchartDiagramConfig"),
        ("gantt", "gantt", "GanttDiagramConfig"),
        ("gitGraph", "gitGraph", "GitGraphDiagramConfig"),
        ("ishikawa-beta", "ishikawa", "IshikawaDiagramConfig"),
        ("journey", "journey", "JourneyDiagramConfig"),
        ("kanban", "kanban", "KanbanDiagramConfig"),
        ("mindmap", "mindmap", "MindmapDiagramConfig"),
        ("packet", "packet", "PacketDiagramConfig"),
        ("pie", "pie", "PieDiagramConfig"),
        ("radar-beta", "radar", "RadarDiagramConfig"),
        ("railroad-ebnf-beta", "railroad", "RailroadDiagramConfig"),
        ("requirementDiagram", "requirement", "RequirementDiagramConfig"),
        ("sankey", "sankey", "SankeyDiagramConfig"),
        ("sequenceDiagram", "sequence", "SequenceDiagramConfig"),
        ("stateDiagram-v2", "state", "StateDiagramConfig"),
        ("swimlane-beta", "swimlane", "SwimlaneDiagramConfig"),
        ("timeline", "timeline", "TimelineDiagramConfig"),
        ("treeView-beta", "treeView", "TreeViewDiagramConfig"),
        ("venn-beta", "venn", "VennDiagramConfig"),
        ("wardley-beta", "wardley-beta", "WardleyDiagramConfig"),
    ]


def test_registry_returns_detailed_information_by_mermaid_syntax_id() -> None:
    diagram = Application.create().diagram_info("sequenceDiagram")

    assert diagram.name == "Sequence diagram"
    assert diagram.id == "sequenceDiagram"
    assert diagram.config_key == "sequence"


def test_every_registered_diagram_renders_its_public_kind_as_the_header() -> None:
    application = Application.create()

    for info in application.available_diagrams():
        diagram = application.create_diagram(info.id)
        source = application.render(diagram)
        body = source.split("---\n", maxsplit=2)[2]
        header = body.splitlines()[0]

        assert header == info.id or header.startswith(f"{info.id} ")


def test_registry_explains_unknown_diagram_ids() -> None:
    with pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
        Application.create().diagram_info("unknown")
