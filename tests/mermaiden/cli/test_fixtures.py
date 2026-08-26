from pathlib import Path

from mermaiden.cli import MermaidenCli


class TestDiagramFixtures:
    def test_exposes_one_populated_fixture_for_every_catalogued_diagram(self) -> None:
        diagrams = MermaidenCli.create().rendered_diagrams()

        assert tuple(diagrams) == (
            "flowchart",
            "treeview",
            "classdiagram",
            "architecture",
            "sequence",
            "requirement",
            "mindmap",
            "pie",
            "timeline",
            "sankey",
            "journey",
            "ishikawa",
            "venn",
            "radar",
            "block",
            "packet",
            "er",
            "eventmodeling",
            "gantt",
            "gitgraph",
            "c4",
            "cynefin",
            "kanban",
            "railroad",
            "wardley",
            "state",
            "swimlane",
        )
        assert all(source.startswith("---\nconfig:\n") for source in diagrams.values())
        assert all(source.endswith("\n") for source in diagrams.values())

    def test_writes_every_available_fixture_without_changing_its_source(self, tmp_path: Path) -> None:
        cli = MermaidenCli.create()
        expected = cli.rendered_diagrams()
        output = tmp_path / "fixtures"

        paths = cli.write_fixtures(output)

        assert {path.name for path in paths} == {f"{name}.mmd" for name in expected}
        assert {path.stem: path.read_text(encoding="utf-8") for path in paths} == expected
