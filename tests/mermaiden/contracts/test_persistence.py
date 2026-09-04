import pytest

from mermaiden import Application


class TestPersistence:
    def test_rejects_a_snapshot_from_an_unsupported_contract_version(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.execute(diagram, "add_block", {"id": "example", "label": "Example"})
        payload = application.snapshot(diagram).to_dict()
        payload["version"] = 1
        del payload["configuration"]

        with pytest.raises(RuntimeError, match="version '1'; expected version '3'"):
            application.restore(payload)
