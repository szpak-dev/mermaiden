from collections.abc import Mapping
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError
from wireup import injectable

from .domain import SnapshotContract, SnapshotError, SnapshotTypeRegistry


class SnapshotBoolean(RootModel[bool]):
    model_config = ConfigDict(frozen=True, strict=True)


class SnapshotMapping(RootModel[Mapping[str, object]]):
    model_config = ConfigDict(frozen=True, strict=True)


class SnapshotMappings(RootModel[list[Mapping[str, object]]]):
    model_config = ConfigDict(frozen=True, strict=True)


class SnapshotString(RootModel[str]):
    model_config = ConfigDict(frozen=True, strict=True)


class SnapshotEncodedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True, strict=True)

    discriminator: str = Field(alias="$type")
    fields: Mapping[str, "SnapshotEncodedValue"]

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> BaseModel:
        model_type = types.resolve_model(contract.owner, self.discriminator)
        expected_fields = set(model_type.model_fields)
        received_fields = set(self.fields)
        if received_fields != expected_fields:
            missing = sorted(expected_fields - received_fields)
            extra = sorted(received_fields - expected_fields)
            details = [
                *(f"missing '{name}'" for name in missing),
                *(f"unsupported '{name}'" for name in extra),
            ]
            raise SnapshotError(f"Snapshot fields are invalid: {', '.join(details)}.")
        parameters = {name: item.decode(types, contract) for name, item in self.fields.items()}
        return model_type(**parameters)


class SnapshotEncodedEnum(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True, strict=True)

    discriminator: str = Field(alias="$enum")
    value: object

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> object:
        enum_type = types.resolve_enum(contract.owner, self.discriminator)
        return enum_type(self.value)


class SnapshotEncodedMapping(RootModel[Mapping[str, "SnapshotEncodedValue"]]):
    model_config = ConfigDict(frozen=True, strict=True)

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> object:
        return {name: item.decode(types, contract) for name, item in self.root.items()}


class SnapshotEncodedSequence(RootModel[tuple["SnapshotEncodedValue", ...]]):
    model_config = ConfigDict(frozen=True)

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> object:
        return [item.decode(types, contract) for item in self.root]


class SnapshotEncodedScalar(RootModel[None | bool | int | float | str]):
    model_config = ConfigDict(frozen=True, strict=True)

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> object:
        return self.root


class SnapshotEncodedValue(
    RootModel[
        Annotated[
            SnapshotEncodedModel
            | SnapshotEncodedEnum
            | SnapshotEncodedMapping
            | SnapshotEncodedSequence
            | SnapshotEncodedScalar,
            Field(union_mode="left_to_right"),
        ]
    ]
):
    model_config = ConfigDict(frozen=True, strict=True)

    def decode(self, types: SnapshotTypeRegistry, contract: SnapshotContract) -> object:
        return self.root.decode(types, contract)


@injectable
class SnapshotValueValidator:
    def boolean(self, value: object, name: str) -> bool:
        try:
            return SnapshotBoolean.model_validate(value).root
        except ValidationError as error:
            raise SnapshotError(f"Snapshot '{name}' must be a boolean.") from error

    def mapping(self, value: object, name: str) -> Mapping[str, object]:
        try:
            return SnapshotMapping.model_validate(value).root
        except ValidationError as error:
            raise SnapshotError(f"Snapshot '{name}' must be an object.") from error

    def objects(self, value: object, name: str) -> tuple[Mapping[str, object], ...]:
        try:
            return tuple(SnapshotMappings.model_validate(value).root)
        except ValidationError as error:
            raise SnapshotError(f"Snapshot '{name}' must be an array of objects.") from error

    def string(self, value: object, name: str) -> str:
        try:
            return SnapshotString.model_validate(value).root
        except ValidationError as error:
            raise SnapshotError(f"Snapshot '{name}' must be a string.") from error

    def encoded(self, value: object) -> SnapshotEncodedValue:
        return SnapshotEncodedValue.model_validate(value)
