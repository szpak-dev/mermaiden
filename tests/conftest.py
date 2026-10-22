import pytest


class AuntieOrder:
    def key(self, item: pytest.Item) -> int:
        name = item.name.lower()
        if any(
            term in name
            for term in (
                "attack",
                "bad_",
                "cannot",
                "duplicate",
                "fail",
                "invalid",
                "reject",
                "require",
                "unsafe",
                "unknown",
                "unsupported",
            )
        ):
            return 0
        if any(term in name for term in ("determin", "invariant", "preserv", "stable", "unchanged")):
            return 1
        if any(term in name for term in ("atomic", "batch", "interrupt", "rolls_back")):
            return 2
        if any(term in name for term in ("cascade", "cleanup", "delete", "remove")):
            return 3
        if any(term in name for term in ("recover", "restore", "round_trip", "reopen")):
            return 4
        return 5


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    items.sort(key=AuntieOrder().key)
