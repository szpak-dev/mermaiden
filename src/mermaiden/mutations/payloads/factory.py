from collections.abc import Mapping
from typing import Annotated, Literal, cast

from pydantic import Field, RootModel
from wireup import injectable

from ...core.annotation import Annotation
from ...core.element import Element
from ...core.model import ClassifiedValueModel, ValueModel
from ...core.relation import Relation
from ...domain import CommandPayloadType
from ..domain import MutationPayloadFactory
from .models import MutationChanges


@injectable(as_type=MutationPayloadFactory, lifetime="scoped")
class PydanticMutationPayloadFactory(MutationPayloadFactory):
    def element(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Element]],
    ) -> CommandPayloadType:
        return self._create(diagram_name, "update_element", object_types)

    def relation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Relation]],
    ) -> CommandPayloadType:
        return self._create(diagram_name, "update_relation", object_types)

    def annotation(
        self,
        diagram_name: str,
        object_types: Mapping[str, type[Annotation]],
    ) -> CommandPayloadType:
        return self._create(diagram_name, "update_annotation", object_types)

    def _create(
        self,
        diagram_name: str,
        command_name: str,
        object_types: Mapping[str, type[ClassifiedValueModel]],
    ) -> CommandPayloadType:
        variants = tuple(
            self._variant(diagram_name, command_name, kind, object_type) for kind, object_type in object_types.items()
        )
        if not variants:
            raise ValueError(f"Command '{command_name}' has no object payloads.")
        if len(variants) == 1:
            root_type = RootModel[variants[0]]
        else:
            union = variants[0] | variants[1]
            for variant in variants[2:]:
                union |= variant
            root_type = RootModel[Annotated[union, Field(discriminator="kind")]]
        name = f"{diagram_name}{self._pascal_case(command_name)}Payload"
        return cast(CommandPayloadType, type(name, (root_type,), {"__module__": __name__}))

    def _variant(
        self,
        diagram_name: str,
        command_name: str,
        kind: str,
        object_type: type[ClassifiedValueModel],
    ) -> type[ValueModel]:
        change_annotations = {
            name: field.rebuild_annotation()
            for name, field in object_type.model_fields.items()
            if name != "id" and name != "elements"
        }
        change_namespace: dict[str, object] = {
            "__module__": __name__,
            "__annotations__": change_annotations,
            **dict.fromkeys(change_annotations),
        }
        changes = cast(
            type[MutationChanges],
            type(
                f"{diagram_name}{self._pascal_case(kind)}Changes",
                (MutationChanges,),
                change_namespace,
            ),
        )
        payload_namespace: dict[str, object] = {
            "__module__": __name__,
            "__annotations__": {
                "id": object_type.model_fields["id"].rebuild_annotation(),
                "kind": Literal[kind],
                "changes": changes,
            },
            "id": ...,
            "kind": ...,
            "changes": ...,
        }
        return cast(
            type[ValueModel],
            type(
                f"{diagram_name}{self._pascal_case(kind)}{self._pascal_case(command_name)}Payload",
                (ValueModel,),
                payload_namespace,
            ),
        )

    def _pascal_case(self, value: str) -> str:
        return "".join(part.capitalize() for part in value.split("_"))
