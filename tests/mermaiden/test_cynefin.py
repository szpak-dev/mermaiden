import json

from mermaiden.application import Application, DiagramCommand


class TestCynefin:
    def test_renders_every_domain_in_canonical_order(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        for id, label, domain in (
            ("clear", "Clear item", "clear"),
            ("confusion", "Confusion item", "confusion"),
            ("complex", "Complex item", "complex"),
            ("chaotic", "Chaotic item", "chaotic"),
            ("complicated", "Complicated item", "complicated"),
        ):
            application.apply(
                diagram,
                DiagramCommand("add_item", {"id": id, "label": label, "domain": domain}),
            )

        body = application.render(diagram).split("---\n", maxsplit=2)[2]

        assert body == (
            "cynefin-beta\n"
            "complex\n"
            '  "Complex item"\n'
            "complicated\n"
            '  "Complicated item"\n'
            "clear\n"
            '  "Clear item"\n'
            "chaotic\n"
            '  "Chaotic item"\n'
            "confusion\n"
            '  "Confusion item"\n'
        )

    def test_omits_empty_domains(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.apply(
            diagram,
            DiagramCommand("add_item", {"id": "complex", "label": "Complex item", "domain": "complex"}),
        )
        application.apply(
            diagram,
            DiagramCommand("add_item", {"id": "clear", "label": "Clear item", "domain": "clear"}),
        )

        body = application.render(diagram).split("---\n", maxsplit=2)[2]

        assert body == (
            "cynefin-beta\n"
            "complex\n"
            '  "Complex item"\n'
            "clear\n"
            '  "Clear item"\n'
        )

    def test_preserves_domains_and_transitions_through_snapshot_restoration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.apply(
            diagram,
            DiagramCommand("add_item", {"id": "complex", "label": "Investigate", "domain": "complex"}),
        )
        application.apply(
            diagram,
            DiagramCommand("add_item", {"id": "complicated", "label": "Analyze", "domain": "complicated"}),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "add_transition",
                {
                    "id": "pattern",
                    "source_id": "complex",
                    "target_id": "complicated",
                    "label": "Pattern identified",
                },
            ),
        )
        source = application.render(diagram)

        snapshot = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        restored = application.restore(snapshot)

        assert application.render(restored) == source
        assert 'complex --> complicated : "Pattern identified"' in source
