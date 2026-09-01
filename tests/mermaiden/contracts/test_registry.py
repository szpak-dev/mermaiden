import pytest

from mermaiden import Application


class TestDiagramRegistry:
    def test_lists_every_implemented_diagram_with_mermaid_metadata(self) -> None:
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

    def test_returns_detailed_information_by_mermaid_syntax_id(self) -> None:
        diagram = Application.create().diagram_info("sequenceDiagram")

        assert diagram.name == "Sequence diagram"
        assert diagram.id == "sequenceDiagram"
        assert diagram.config_key == "sequence"

    def test_every_registered_empty_diagram_is_a_persistable_but_non_renderable_draft(self) -> None:
        application = Application.create()

        for info in application.available_diagrams():
            diagram = application.create_diagram(info.id)

            assert application.snapshot(diagram).to_dict()["draft"] is True
            with pytest.raises(RuntimeError, match=f"Cannot render invalid diagram '{info.id}'"):
                application.render(diagram)

    def test_explains_unknown_diagram_ids(self) -> None:
        with pytest.raises(KeyError, match="Unknown diagram 'unknown'"):
            Application.create().diagram_info("unknown")
