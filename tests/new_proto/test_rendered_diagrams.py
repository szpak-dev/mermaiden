from new_proto.application import Application


def test_rendered_diagrams_cover_every_supported_building_block() -> None:
    diagrams = Application.create().rendered_diagrams()

    expected = {
        "flowchart": (
            "flowchart TD",
            "shape: circle",
            "shape: diam",
            "shape: rect",
            "shape: dbl-circ",
            "@-->",
            "yes",
            "Process work",
        ),
        "treeview": (
            "treeView-beta",
            "root/",
            "src/ icon(folder)",
            "tests/ icon(test)",
            "README.md :::highlight ## Documentation",
        ),
        "classdiagram": (
            "classDiagram",
            "namespace domain",
            "class Animal",
            "<|--",
            "o--",
            "<..",
            'note for Pond "Aggregate"',
        ),
        "architecture": (
            "architecture-beta",
            "group clients[Clients]",
            "service api[API] in platform",
            "junction events in platform",
            "web:R --> L:api",
            "Persistent storage",
        ),
        "sequence": (
            "sequenceDiagram",
            "actor user as User",
            'participant web@{ "type": "boundary" } as Web',
            'participant api@{ "type": "control" } as API',
            'participant database@{ "type": "database" } as Database',
            'create participant worker@{ "type": "entity" } as Worker',
            "loop retry",
            "par effects",
            "Note left of user: Caller",
            "Note right of web: Gateway",
        ),
    }

    assert diagrams.keys() == expected.keys()
    for name, fragments in expected.items():
        source = diagrams[name]
        assert source.startswith("---\nconfig:\n  wrap: true\n---\n")
        for fragment in fragments:
            assert fragment in source
