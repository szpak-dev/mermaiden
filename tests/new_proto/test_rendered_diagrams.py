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
        "block": ("block", "columns 3", 'frontend["Frontend"]', "space", "block:backend", "columns 2", 'api["API"]'),
        "er": ("erDiagram", "CUSTOMER ||--o{ ORDER : places", "int id PK"),
        "gantt": ("gantt", "title Release plan", "section Delivery", "Design : done, design, 2026-08-01, 2d"),
        "gitgraph": (
            "gitGraph",
            'commit id: "ZERO" tag: "v1.0.0"',
            "branch develop order: 1",
            "checkout develop",
            'commit id: "FEATURE" type: HIGHLIGHT',
            "checkout main",
        ),
        "c4": (
            "C4Context",
            'Person(customer, "Customer", "A personal banking customer")',
            'System(banking, "Internet Banking System", "Provides online banking", "Python")',
            'SystemDb(accounts, "Accounts Database", "Stores account balances", "PostgreSQL")',
            'Rel(customer, banking, "Uses")',
        ),
        "cynefin": (
            "cynefin-beta",
            "complex",
            '"Investigate root cause"',
            "complicated",
            '"Analyze performance data"',
            'complex --> complicated : "Pattern identified"',
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
        "requirement": (
            "requirementDiagram",
            "functionalRequirement r_v_login {",
            'id: "REQ-002"',
            'text: "Users can sign in."',
            "performanceRequirement r_v_latency {",
            "designConstraint r_v_policy {",
            "element r_v_service {",
            'docref: "docs/service.md"',
            "r_v_service - satisfies -> r_v_system",
            "r_v_test_suite - verifies -> r_v_login",
        ),
        "mindmap": (
            "mindmap",
            '"Modwire"',
            'm_v_contracts["Contracts"]',
            'm_v_services("Services")',
            'm_v_runtime(("Runtime"))',
            'm_v_warning))"Important"((',
            'm_v_cloud)"Cloud"(',
            'm_v_quality{{"Quality"}}',
        ),
        "pie": (
            "pie showData",
            'title "Adopted pets"',
            '"Dogs" : 386',
            '"Cats" : 85',
            '"Rats" : 15',
        ),
        "packet": ("packet", "title UDP packet", '+16: "Source port"', '32-47: "Length"'),
        "timeline": ("timeline", "title Modwire history", "section Foundation", "2024 : Prototype : First release"),
        "sankey": ("sankey", '"Electricity grid","Industry",342.165', '"Electricity grid","Homes",113.726'),
        "journey": ("journey", "title Working day", "section Go to work", "Make tea: 5: Me", "Do work: 1: Me, Cat"),
        "venn": (
            "venn-beta",
            'set frontend["Frontend"]:20',
            'text react["React"]',
            'union frontend,backend["Shared"]:3',
            'text openapi["OpenAPI"]',
        ),
        "radar": (
            "radar-beta",
            "title Restaurant comparison",
            'axis food["Food quality"], axis service["Service"], axis price["Price"]',
            'curve restaurant_a["Restaurant A"]{ 4, 3, 2 }',
            "showLegend true",
            "max 5",
            "min 0",
            "graticule polygon",
            "ticks 5",
        ),
        "state": (
            "stateDiagram-v2 TD",
            'state "Still" as s_v_still',
            "state s_v_decision <<choice>>",
            "state s_v_fork <<fork>>",
            "state s_v_join <<join>>",
            's_v_active: "Active"',
            "state s_v_active {",
            "[*] --> s_v_num_lock_off",
            'note right of s_v_moving : "A moving system"',
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
        if name == "pie":
            assert source.startswith("---\nconfig:\n  wrap: true\n  pie: {")
        elif name == "mindmap":
            assert source.startswith(
                "---\nconfig:\n  wrap: true\n"
                '  mindmap: {"useMaxWidth": true, "padding": 10, '
                '"maxNodeWidth": 200, "layoutAlgorithm": "cose-bilkent"}\n---\n'
            )
        elif name == "requirement":
            assert source.startswith("---\nconfig:\n  wrap: true\n  requirement: {")
        elif name == "state":
            assert source.startswith(
                "---\nconfig:\n  wrap: true\n"
                '  state: {"titleTopMargin": 25, "useMaxWidth": true, "defaultRenderer": "dagre-wrapper"}\n---\n'
            )
        elif name == "swimlane":
            assert source.startswith(
                "---\nconfig:\n  wrap: true\n"
                '  swimlane: {"lineHops": "arc", "ignoreCrossLaneEdges": true, '
                '"optimizeRanksByCrossings": true, "automaticLaneOrdering": false}\n---\n'
            )
        elif name == "venn":
            assert source.startswith(
                "---\nconfig:\n  wrap: true\n"
                '  venn: {"width": 800, "height": 450, "padding": 8, "useDebugLayout": false}\n---\n'
            )
        elif name == "block":
            assert source.startswith("---\nconfig:\n  wrap: true\n  block: {\"padding\": 8}\n---\n")
        elif name == "er":
            assert source.startswith("---\nconfig:\n  wrap: true\n  er: {")
        elif name == "gantt":
            assert source.startswith("---\nconfig:\n  wrap: true\n  gantt: {")
        elif name == "gitgraph":
            assert source.startswith("---\nconfig:\n  wrap: true\n  gitGraph: {")
        elif name == "c4":
            assert source.startswith("---\nconfig:\n  wrap: true\n  c4: {}\n---\n")
        elif name == "cynefin":
            assert source.startswith("---\nconfig:\n  wrap: true\n  cynefin: {")
        elif name == "packet":
            assert source.startswith("---\nconfig:\n  wrap: true\n  packet: {")
        elif name == "radar":
            assert source.startswith("---\nconfig:\n  wrap: true\n  radar: {")
        else:
            assert source.startswith("---\nconfig:\n  wrap: true\n---\n")
        for fragment in fragments:
            assert fragment in source
