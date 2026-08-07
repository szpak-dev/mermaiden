import pytest

from new_proto.application import Application


def test_registry_lists_every_implemented_diagram_with_mermaid_metadata() -> None:
    diagrams = Application.create().available_diagrams()

    assert [(item.id, item.config_key, item.schema_definition) for item in diagrams] == [
        ("architecture-beta", "architecture", "ArchitectureDiagramConfig"),
        ("classDiagram", "class", "ClassDiagramConfig"),
        ("flowchart", "flowchart", "FlowchartDiagramConfig"),
        ("mindmap", "mindmap", "MindmapDiagramConfig"),
        ("pie", "pie", "PieDiagramConfig"),
        ("requirementDiagram", "requirement", "RequirementDiagramConfig"),
        ("sankey", "sankey", "SankeyDiagramConfig"),
        ("sequenceDiagram", "sequence", "SequenceDiagramConfig"),
        ("stateDiagram-v2", "state", "StateDiagramConfig"),
        ("swimlane-beta", "swimlane", "SwimlaneDiagramConfig"),
        ("timeline", "timeline", "TimelineDiagramConfig"),
        ("treeView-beta", "treeView", "TreeViewDiagramConfig"),
    ]
    assert all(item.diagram_type.syntax == item.id for item in diagrams)


def test_registry_returns_detailed_information_by_mermaid_syntax_id() -> None:
    diagram = Application.create().diagram_info("sequenceDiagram")

    assert diagram.name == "Sequence diagram"
    assert diagram.syntax_id == "sequenceDiagram"
    assert diagram.config_key == "sequence"


def test_registry_returns_detailed_information_by_mermaid_config_key() -> None:
    diagram = Application.create().diagram_info_for_config("architecture")

    assert diagram.id == "architecture-beta"
    assert diagram.schema_definition == "ArchitectureDiagramConfig"


def test_registry_explains_unknown_diagram_ids() -> None:
    with pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
        Application.create().diagram_info("unknown")
