from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, RootModel, model_validator

from ...core.domain import Entity, ValueModel


class InvalidPacketRange(ValueError):
    pass


class PacketRange(ValueModel):
    kind: Literal["range"]
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def require_ordered_range(self) -> Self:
        if self.end < self.start:
            raise InvalidPacketRange("Packet range end must be at least its start.")
        return self


class PacketBitCount(ValueModel):
    kind: Literal["bits"]
    bits: int = Field(gt=0)


class PacketPosition(RootModel[PacketRange | PacketBitCount]):
    model_config = ConfigDict(frozen=True)

    root: Annotated[PacketRange | PacketBitCount, Field(discriminator="kind")]


class PacketField(Entity):
    position: PacketPosition
