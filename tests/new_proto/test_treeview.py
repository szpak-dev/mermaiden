import pytest

from new_proto.application import Application
from new_proto.core import ChangeRejected
from new_proto.diagrams.flowchart.diagram import Flowchart
from new_proto.diagrams.registry import DiagramRegistry
from new_proto.diagrams.treeview.diagram import TreeView
from new_proto.mermaid.service import MermaidRenderer


def test_mermaid_renderer_wraps_treeview_and_flowchart() -> None:
    container = Application.create()
    with container.enter_scope() as scope:
        registry = scope.get(DiagramRegistry)
        tree = registry.get("treeView-beta").diagram
        assert isinstance(tree, TreeView)
        tree.add_item("project", "project/")
        tree.add_item("src", "src/")
        tree.add_item("app", "App.tsx")
        tree.add_branch("project-src", "project", "src")
        tree.add_branch("src-app", "src", "app")
        tree.add_annotation("app-info", "app", highlight=True, icon="logos:react", description="main")

        assert scope.get(MermaidRenderer).render(tree) == (
            "---\nconfig:\n  wrap: true\n---\ntreeView-beta\n"
            "    project/\n        src/\n            App.tsx :::highlight icon(logos:react) ## main\n"
        )

        flowchart = registry.get("flowchart").diagram
        assert isinstance(flowchart, Flowchart)
        flowchart.add_start("start", "Start")
        flowchart.add_end("end", "End")
        flowchart.add_flow("flow", "start", "end")
        assert (
            scope.get(MermaidRenderer).render(flowchart).startswith("---\nconfig:\n  wrap: true\n---\nflowchart TD\n")
        )


def test_treeview_rejects_cycles() -> None:
    container = Application.create()
    with container.enter_scope() as scope:
        tree = scope.get(DiagramRegistry).get("treeView-beta").diagram
        assert isinstance(tree, TreeView)
        tree.add_item("one", "one")
        tree.add_item("two", "two")
        tree.add_branch("one-two", "one", "two")

        with pytest.raises(ChangeRejected, match="must not form a cycle"):
            tree.add_branch("two-one", "two", "one")
