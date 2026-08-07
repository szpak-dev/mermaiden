from pathlib import Path

import pytest

from mermaiden.application import Application
from mermaiden.mermaid.application import MermaidApplication


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
    assert all(item.diagram_type.definition.syntax == item.id for item in diagrams)


def test_registry_returns_detailed_information_by_mermaid_syntax_id() -> None:
    diagram = Application.create().diagram_info("sequenceDiagram")

    assert diagram.name == "Sequence diagram"
    assert diagram.syntax_id == "sequenceDiagram"
    assert diagram.config_key == "sequence"


def test_every_registered_diagram_has_an_explicit_document_template() -> None:
    renderer = MermaidApplication()
    templates = set(renderer.environment.list_templates())

    assert {
        f"templates/syntax/{item.id}/document.mmd.j2"
        for item in Application.create().available_diagrams()
    } == {
        template
        for template in templates
        if template.startswith("templates/syntax/") and template.endswith("/document.mmd.j2")
    }


def test_every_diagram_uses_a_single_constraints_module() -> None:
    diagrams = Path(__file__).parents[2] / "src" / "mermaiden" / "diagrams"

    assert all(path.with_name("constraints.py").is_file() for path in diagrams.glob("*/diagram.py"))
    assert not tuple(diagrams.glob("*/constraints"))


def test_registry_explains_unknown_diagram_ids() -> None:
    with pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
        Application.create().diagram_info("unknown")
