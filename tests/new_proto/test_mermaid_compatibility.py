from new_proto.application import Application


def test_application_validates_every_registered_diagram_against_pinned_mermaid_schema() -> None:
    report = Application.create().compatibility_report()

    assert report.lock.mermaid_version == "11.16.0"
    assert not report.valid
    assert any(item.config_key == "gantt" for item in report.missing_diagrams)
    assert [(item.diagram_id, item.config_key, item.schema_definition) for item in report.diagrams] == [
        ("architecture-beta", "architecture", "ArchitectureDiagramConfig"),
        ("classDiagram", "class", "ClassDiagramConfig"),
        ("flowchart", "flowchart", "FlowchartDiagramConfig"),
        ("journey", "journey", "JourneyDiagramConfig"),
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
    configurations = {item.diagram_id: item.configuration.values for item in report.diagrams}
    assert all(
        values == {"wrap": True}
        for diagram_id, values in configurations.items()
        if diagram_id not in {"mindmap", "pie", "requirementDiagram", "stateDiagram-v2", "swimlane-beta"}
    )
    assert configurations["swimlane-beta"] == {
        "wrap": True,
        "swimlane": {
            "lineHops": "arc",
            "ignoreCrossLaneEdges": True,
            "optimizeRanksByCrossings": True,
            "automaticLaneOrdering": False,
        },
    }
    assert configurations["stateDiagram-v2"] == {
        "wrap": True,
        "state": {"titleTopMargin": 25, "useMaxWidth": True, "defaultRenderer": "dagre-wrapper"},
    }
    assert configurations["requirementDiagram"]["requirement"]["useMaxWidth"] is True
    assert configurations["mindmap"]["mindmap"] == {
        "useMaxWidth": True,
        "padding": 10,
        "maxNodeWidth": 200,
        "layoutAlgorithm": "cose-bilkent",
    }
    assert configurations["pie"]["pie"]["donutHole"] == 0
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
