import pytest

from new_proto.application import Application
from new_proto.mermaid.service import MermaidRenderer


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
    assert all(item.diagram_type.syntax == item.id for item in diagrams)


def test_registry_returns_detailed_information_by_mermaid_syntax_id() -> None:
    diagram = Application.create().diagram_info("sequenceDiagram")

    assert diagram.name == "Sequence diagram"
    assert diagram.syntax_id == "sequenceDiagram"
    assert diagram.config_key == "sequence"


def test_every_registered_diagram_has_an_explicit_document_template() -> None:
    renderer = MermaidRenderer()
    templates = set(renderer.environment.list_templates())

    assert {
        renderer._document_template(item.diagram)
        for item in Application.create().available_diagrams()
    } == {
        template
        for template in templates
        if template.startswith("templates/syntax/") and template.endswith("/document.mmd.j2")
    }


def test_registry_returns_detailed_information_by_mermaid_config_key() -> None:
    diagram = Application.create().diagram_info_for_config("architecture")

    assert diagram.id == "architecture-beta"
    assert diagram.schema_definition == "ArchitectureDiagramConfig"


def test_registry_explains_unknown_diagram_ids() -> None:
    with pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
        Application.create().diagram_info("unknown")
