import pytest

from new_proto.application import Application
from new_proto.diagrams.registry import DiagramRegistry


def test_registry_lists_every_implemented_diagram_with_mermaid_metadata() -> None:
    container = Application.create()
    with container.enter_scope() as scope:
        diagrams = scope.get(DiagramRegistry).available()

    assert [(item.id, item.config_key, item.schema_definition) for item in diagrams] == [
        ("architecture-beta", "architecture", "ArchitectureDiagramConfig"),
        ("classDiagram", "class", "ClassDiagramConfig"),
        ("flowchart", "flowchart", "FlowchartDiagramConfig"),
        ("sequenceDiagram", "sequence", "SequenceDiagramConfig"),
        ("treeView-beta", "treeView", "TreeViewDiagramConfig"),
    ]
    assert all(item.diagram_type.syntax == item.id for item in diagrams)


def test_registry_returns_detailed_information_by_mermaid_syntax_id() -> None:
    container = Application.create()
    with container.enter_scope() as scope:
        diagram = scope.get(DiagramRegistry).get("sequenceDiagram")

    assert diagram.name == "Sequence diagram"
    assert diagram.syntax_id == "sequenceDiagram"
    assert diagram.config_key == "sequence"


def test_registry_explains_unknown_diagram_ids() -> None:
    container = Application.create()
    with container.enter_scope() as scope, pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
        scope.get(DiagramRegistry).get("unknown")
