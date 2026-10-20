import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from inspect import isabstract
from typing import Annotated, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, RootModel, TypeAdapter
from wireup import injectable

from ...core.naming import ClassName
from ...runtime.snapshot.domain import SnapshotContract, SnapshotError, SnapshotType, SnapshotTypeRegistry
from ..application import DiagramsApplication


class SnapshotEnumRegistration(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    value_type: type[Enum]

    def register(
        self,
        owner: str,
        registered: dict[type[object], SnapshotType],
        expanded: set[type[object]],
        pending: list[object],
    ) -> None:
        if self.value_type in expanded:
            return
        expanded.add(self.value_type)
        registered.setdefault(
            self.value_type,
            SnapshotType(
                f"mermaiden/enum/{owner}/{ClassName(self.value_type).snake_case}",
                self.value_type,
            ),
        )


class SnapshotModelRegistration(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True)

    value_type: type[BaseModel]

    def register(
        self,
        owner: str,
        registered: dict[type[object], SnapshotType],
        expanded: set[type[object]],
        pending: list[object],
    ) -> None:
        if self.value_type in expanded:
            return
        expanded.add(self.value_type)
        if isabstract(self.value_type):
            return
        registered.setdefault(
            self.value_type,
            SnapshotType(
                f"mermaiden/value/{owner}/{ClassName(self.value_type).snake_case}",
                self.value_type,
            ),
        )
        pending.extend(field.annotation for field in self.value_type.model_fields.values())


class SnapshotIgnoredRegistration(BaseModel):
    model_config = ConfigDict(frozen=True)

    value_type: object

    def register(
        self,
        owner: str,
        registered: dict[type[object], SnapshotType],
        expanded: set[type[object]],
        pending: list[object],
    ) -> None:
        return None


class SnapshotRegistration(RootModel[object]):
    model_config = ConfigDict(frozen=True, strict=True)

    root: Annotated[
        SnapshotEnumRegistration | SnapshotModelRegistration | SnapshotIgnoredRegistration,
        Field(union_mode="left_to_right"),
    ]


class SnapshotModelClass(RootModel[type[BaseModel]]):
    model_config = ConfigDict(frozen=True, strict=True)


class SnapshotEnumClass(RootModel[type[Enum]]):
    model_config = ConfigDict(frozen=True, strict=True)


@injectable(as_type=SnapshotTypeRegistry, lifetime="scoped")
@dataclass(frozen=True)
class DiagramSnapshotRegistry(SnapshotTypeRegistry):
    diagrams: DiagramsApplication

    def contract(self, owner: str) -> SnapshotContract:
        try:
            return self.contracts[owner]
        except KeyError:
            raise SnapshotError(f"Snapshot diagram kind '{owner}' is not registered.") from None

    def reference(self, owner: str, value_type: type[object]) -> str:
        contract = self.contract(owner)
        match = next((item.discriminator for item in contract.types if item.value_type is value_type), None)
        if match is None:
            raise SnapshotError(f"Snapshot type '{value_type.__name__}' is not registered for '{owner}'.")
        return match

    def registered_type(self, owner: str, discriminator: str) -> type[object]:
        contract = self.contract(owner)
        match = next((item.value_type for item in contract.types if item.discriminator == discriminator), None)
        if match is None:
            raise SnapshotError(f"Snapshot discriminator '{discriminator}' is not registered for '{owner}'.")
        return match

    def resolve_model(self, owner: str, discriminator: str) -> type[BaseModel]:
        return SnapshotModelClass.model_validate(self.registered_type(owner, discriminator)).root

    def resolve_enum(self, owner: str, discriminator: str) -> type[Enum]:
        return SnapshotEnumClass.model_validate(self.registered_type(owner, discriminator)).root

    @cached_property
    def contracts(self) -> dict[str, SnapshotContract]:
        contracts: dict[str, SnapshotContract] = {}
        for info in self.diagrams:
            diagram = self.diagrams.get_diagram(info.id)
            feature = diagram.feature
            roots = (
                self.snapshot_type(info.id, "configuration", type(diagram.configuration)),
                *(self.snapshot_type(info.id, "element", item) for item in feature.elements),
                *(self.snapshot_type(info.id, "relation", item) for item in feature.relations),
                *(self.snapshot_type(info.id, "annotation", item) for item in feature.annotations),
            )
            registered = {item.value_type: item for item in roots}
            expanded: set[type[object]] = set()
            pending: list[object] = [*(item.value_type for item in roots)]
            pending.extend(item.annotation for item in feature.snapshot_properties)
            while pending:
                annotation = pending.pop()
                origin = get_origin(annotation)
                if origin is Annotated:
                    pending.append(get_args(annotation)[0])
                    continue
                if origin is not None:
                    pending.extend(get_args(annotation))
                    continue
                registration = SnapshotRegistration.model_validate({"value_type": annotation}).root
                registration.register(info.id, registered, expanded, pending)

            discriminators = [item.discriminator for item in registered.values()]
            if len(discriminators) != len(set(discriminators)):
                raise RuntimeError(f"Snapshot discriminators for '{info.id}' are not unique.")
            contracts[info.id] = SnapshotContract(
                owner=info.id,
                configuration=roots[0],
                elements=roots[1 : 1 + len(feature.elements)],
                relations=roots[1 + len(feature.elements) : 1 + len(feature.elements) + len(feature.relations)],
                annotations=roots[1 + len(feature.elements) + len(feature.relations) :],
                values=tuple(item for item in registered.values() if "/value/" in item.discriminator),
                enums=tuple(item for item in registered.values() if "/enum/" in item.discriminator),
                properties={item.name: item.annotation for item in feature.snapshot_properties},
            )
        return contracts

    @cached_property
    def fingerprint(self) -> str:
        document = {
            owner: {
                "types": {
                    item.discriminator: self.schema(item.value_type)
                    for item in sorted(contract.types, key=lambda candidate: candidate.discriminator)
                },
                "properties": {
                    name: TypeAdapter(annotation).json_schema()
                    for name, annotation in sorted(contract.properties.items())
                },
            }
            for owner, contract in sorted(self.contracts.items())
        }
        encoded = json.dumps(document, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        return hashlib.sha256(encoded.encode()).hexdigest()

    def snapshot_type(self, owner: str, category: str, value_type: type[object]) -> SnapshotType:
        return SnapshotType(f"mermaiden/{category}/{owner}/{ClassName(value_type).snake_case}", value_type)

    def schema(self, value_type: type[object]) -> object:
        return TypeAdapter(value_type).json_schema()
