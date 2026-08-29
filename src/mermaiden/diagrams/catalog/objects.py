from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from inspect import getmembers, isclass

from wireup import injectable

from ...core.annotation import Annotation
from ...core.element import Element
from ...core.model import ClassifiedValueModel
from ...core.relation import Relation
from ..application import DiagramInfo


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramObjectCatalog:
    def elements(self, info: DiagramInfo) -> dict[str, type[Element]]:
        return self._models(info, "elements", Element)

    def relations(self, info: DiagramInfo) -> dict[str, type[Relation]]:
        return self._models(info, "relations", Relation)

    def annotations(self, info: DiagramInfo) -> dict[str, type[Annotation]]:
        return self._models(info, "annotations", Annotation)

    def schemas(
        self,
        object_types: Mapping[str, type[ClassifiedValueModel]],
    ) -> dict[str, Mapping[str, object]]:
        return {kind: object_type.model_json_schema() for kind, object_type in object_types.items()}

    def _models[ObjectT: ClassifiedValueModel](
        self,
        info: DiagramInfo,
        collection_name: str,
        parent: type[ObjectT],
    ) -> dict[str, type[ObjectT]]:
        package = info.diagram_type.__module__.removesuffix(".diagram")
        module_name = f"{package}.{collection_name}"
        if find_spec(module_name) is None:
            return {}
        module = import_module(module_name)
        return {
            item.kind_for(): item
            for _, item in getmembers(module, isclass)
            if item.__module__ == module.__name__
            if issubclass(item, parent)
            if item is not parent
        }
