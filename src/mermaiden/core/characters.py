import re
from typing import Annotated, ClassVar

from pydantic import ConfigDict, Field, RootModel


class CharacterPolicy(RootModel[str]):
    pattern: ClassVar[str | re.Pattern[str]]
    description: ClassVar[str]
    root: str


class Identifier(CharacterPolicy):
    pattern = r"^[^\s\x00-\x1f\x7f-\x9f](?:[^\x00-\x1f\x7f-\x9f]*[^\s\x00-\x1f\x7f-\x9f])?$"
    description = "Non-empty identifier without surrounding whitespace or control characters."
    root: str = Field(pattern=pattern, description=description, json_schema_extra={"x-character-policy": "Identifier"})


class OptionalIdentifier(CharacterPolicy):
    pattern = r"^(?:[^\s\x00-\x1f\x7f-\x9f](?:[^\x00-\x1f\x7f-\x9f]*[^\s\x00-\x1f\x7f-\x9f])?)?$"
    description = "Empty root reference or an identifier without surrounding whitespace or control characters."
    root: str = Field(
        pattern=pattern,
        description=description,
        json_schema_extra={"x-character-policy": "OptionalIdentifier"},
    )


class Text(CharacterPolicy):
    pattern = r"^[^\s\x00-\x1f\x7f-\x9f](?:[^\x00-\x1f\x7f-\x9f]*[^\s\x00-\x1f\x7f-\x9f])?$"
    description = "Non-empty single-line text without surrounding whitespace or control characters."
    root: str = Field(pattern=pattern, description=description, json_schema_extra={"x-character-policy": "Text"})


class OptionalText(CharacterPolicy):
    pattern = r"^(?:[^\s\x00-\x1f\x7f-\x9f](?:[^\x00-\x1f\x7f-\x9f]*[^\s\x00-\x1f\x7f-\x9f])?)?$"
    description = "Empty or single-line text without surrounding whitespace or control characters."
    root: str = Field(
        pattern=pattern,
        description=description,
        json_schema_extra={"x-character-policy": "OptionalText"},
    )


class NumberText(CharacterPolicy):
    pattern = r"^(?:\d+(?:\.\d+)?|\.\d+)$"
    description = "A non-negative decimal number written as text."
    root: str = Field(pattern=pattern, description=description, json_schema_extra={"x-character-policy": "NumberText"})


class PositiveNumberText(CharacterPolicy):
    pattern = r"^(?:0*[1-9]\d*(?:\.\d+)?|0*\.\d*[1-9]\d*)$"
    description = "A positive decimal number written as text."
    root: str = Field(
        pattern=pattern,
        description=description,
        json_schema_extra={"x-character-policy": "PositiveNumberText"},
    )


class NumberOrText(RootModel[str | float]):
    model_config = ConfigDict(frozen=True)

    root: Annotated[str, Field(pattern=Text.pattern, description=Text.description)] | float


class NumberOrNumericText(NumberOrText):
    root: Annotated[str, Field(pattern=NumberText.pattern, description=NumberText.description)] | float


class PositiveNumberOrNumericText(NumberOrNumericText):
    root: (
        Annotated[str, Field(pattern=PositiveNumberText.pattern, description=PositiveNumberText.description)]
        | Annotated[float, Field(gt=0)]
    )


class Identifiers(RootModel[tuple[Identifier, ...]]):
    root: tuple[Identifier, ...]


class OrderedIdentifiers(Identifiers):
    root: tuple[Identifier, ...] = Field(min_length=1, json_schema_extra={"uniqueItems": True})


class Texts(RootModel[tuple[Text, ...]]):
    root: tuple[Text, ...]


class OneOrTwoIdentifiers(RootModel[tuple[Identifier, ...]]):
    root: tuple[Identifier, ...] = Field(min_length=1, max_length=2)
