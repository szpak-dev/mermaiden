from new_proto.application import Application


def test_application_validates_every_registered_diagram_against_pinned_mermaid_schema() -> None:
    report = Application.create().compatibility_report()

    assert report.lock.mermaid_version == "11.16.0"
    assert not report.valid
    assert any(item.config_key == "mindmap" for item in report.missing_diagrams)
    assert [(item.diagram_id, item.config_key, item.schema_definition) for item in report.diagrams] == [
        ("architecture-beta", "architecture", "ArchitectureDiagramConfig"),
        ("classDiagram", "class", "ClassDiagramConfig"),
        ("flowchart", "flowchart", "FlowchartDiagramConfig"),
        ("sequenceDiagram", "sequence", "SequenceDiagramConfig"),
        ("treeView-beta", "treeView", "TreeViewDiagramConfig"),
    ]
    assert all(item.configuration.values == {"wrap": True} for item in report.diagrams)
    upstream = {item.config_key: item for item in Application.create().mermaid_diagram_configs()}
    assert all(
        item.configuration.schema_definition == upstream[item.configuration.config_key].schema_definition
        for item in report.diagrams
    )


def test_application_lists_diagram_configs_from_mermaid_schema() -> None:
    configs = Application.create().mermaid_diagram_configs()

    mindmap = next(item for item in configs if item.config_key == "mindmap")
    assert mindmap.schema_definition == "MindmapDiagramConfig"
    assert mindmap.schema["type"] == "object"
