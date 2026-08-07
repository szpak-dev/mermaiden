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
        "swimlane": (
            "swimlane-beta TD",
            'subgraph e_v_customer ["Customer"]',
            'e_v_request(["Request service"])',
            'e_v_known{"Known issue?"}',
            'e_v_handoff(("Handoff"))',
            'e_v_known -->|"Yes"| e_v_answer',
            'e_v_known -->|"No"| e_v_investigate',
        ),
    }

    assert diagrams.keys() == expected.keys()
    for name, fragments in expected.items():
        source = diagrams[name]
        if name == "swimlane":
            assert source.startswith(
                "---\nconfig:\n  wrap: true\n"
                '  swimlane: {"lineHops": "arc", "ignoreCrossLaneEdges": true, '
                '"optimizeRanksByCrossings": true, "automaticLaneOrdering": false}\n---\n'
            )
        else:
            assert source.startswith("---\nconfig:\n  wrap: true\n---\n")
        for fragment in fragments:
            assert fragment in source
