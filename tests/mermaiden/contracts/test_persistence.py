import pytest

from mermaiden.application import Application


class TestPersistence:
    def test_rejects_a_snapshot_from_an_unsupported_contract_version(self) -> None:
        application = Application.create()
        payload = application.snapshot(application.create_diagram("block")).to_dict()
        payload["version"] = 1
        del payload["configuration"]

        with pytest.raises(RuntimeError, match="version '1'; expected version '2'"):
            application.restore(payload)
