from importlib import import_module
from typing import Any, cast

from wireup import injectable

from .domain import SnapshotError


@injectable
class SnapshotTypeResolver:
    def resolve(self, reference: str, expected: Any) -> type[Any]:
        module_name, separator, qualified_name = reference.partition(":")
        if not separator or not module_name.startswith("mermaiden."):
            raise SnapshotError(f"Snapshot type '{reference}' is not supported.")
        try:
            item: object = import_module(module_name)
            for name in qualified_name.split("."):
                item = getattr(item, name)
        except (AttributeError, ImportError) as error:
            raise SnapshotError(f"Snapshot type '{reference}' is not available.") from error
        if not isinstance(item, type) or (expected is not object and not issubclass(item, expected)):
            raise SnapshotError(f"Snapshot type '{reference}' is not valid here.")
        return cast(type[Any], item)
