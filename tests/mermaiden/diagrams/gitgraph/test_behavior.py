import json

import pytest

from mermaiden import Application


class TestGitGraph:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gitGraph")
        commands = (
            ("configure", {"mainBranchName": "main", "showCommitLabel": False}),
            ("add_commit", {"id": "initial_example", "label": 'ZERO "root"', "tag": "v1"}),
            ("add_branch", {"id": "develop_example", "label": "develop_example", "order": 1}),
            ("checkout", {"id": "checkout_develop_example", "branch": "develop_example"}),
            ("add_commit", {"id": "feature_example", "label": "FEATURE", "commit_type": "HIGHLIGHT"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("gitGraph").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert 'commit id: "ZERO \\"root\\"" tag: "v1"' in source
        assert "branch develop_example order: 1" in source
        assert "checkout develop_example" in source
        assert 'commit id: "FEATURE" type: HIGHLIGHT' in source
        assert application.render(restored) == source

    def test_rejects_invalid_commit_types_duplicate_ids_and_unknown_branches(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gitGraph")
        application.execute(diagram, "add_commit", {"id": "first_example", "label": "FIRST"})
        with pytest.raises(RuntimeError, match=r"'add_commit' has invalid arguments"):
            application.execute(diagram, "add_commit", {"id": "bad_example", "label": "BAD", "commit_type": "LOUD"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_commit", {"id": "first_example", "label": "AGAIN"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(diagram, "checkout", {"id": "missing_example", "branch": "missing_example"})
