from mermaiden.cli import MermaidenCli


def test_application_renders_treeview_and_flowchart() -> None:
    diagrams = MermaidenCli.create().rendered_diagrams()

    assert diagrams["treeview"] == (
        "---\nconfig:\n  wrap: true\n---\ntreeView-beta\n"
        "root/\n  src/ icon(folder)\n  tests/ icon(test)\n"
        "  README.md :::highlight ## Documentation\n"
    )
    assert diagrams["flowchart"].startswith("---\nconfig:\n  wrap: true\n---\nflowchart TD\n")
