from collections.abc import Mapping
from enum import StrEnum
from typing import Annotated

from pydantic import ConfigDict, Field, InstanceOf, RootModel
from pydantic.json_schema import SkipJsonSchema

from ...core.characters import OptionalText, Text
from ..domain import MermaidDiagramConfiguration, Unconfigured


class SankeyNodeAlignment(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    JUSTIFY = "justify"


class SankeyLabelStyle(StrEnum):
    LEGACY = "legacy"
    OUTLINED = "outlined"


class SankeyNodeColours(
    RootModel[Mapping[str, Annotated[str, Field(pattern=Text.pattern, description=Text.description)]]]
):
    model_config = ConfigDict(frozen=True)


class SankeyDiagramConfiguration(MermaidDiagramConfiguration):
    use_max_width: Annotated[bool, Field(alias="useMaxWidth")] = False
    width: Annotated[float, Field(alias="width")] = 600
    height: Annotated[float, Field(alias="height")] = 400
    link_color: Annotated[
        Annotated[str, Field(pattern=Text.pattern, description=Text.description)], Field(alias="linkColor")
    ] = "gradient"
    node_alignment: Annotated[SankeyNodeAlignment, Field(alias="nodeAlignment")] = SankeyNodeAlignment.JUSTIFY
    show_values: Annotated[bool, Field(alias="showValues")] = True
    prefix: Annotated[
        str, Field(alias="prefix", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
    suffix: Annotated[
        str, Field(alias="suffix", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
    node_width: Annotated[float, Field(alias="nodeWidth")] = 10
    node_padding: Annotated[float, Field(alias="nodePadding")] = 12
    label_style: Annotated[SankeyLabelStyle, Field(alias="labelStyle")] = SankeyLabelStyle.LEGACY
    node_colors: Annotated[
        SankeyNodeColours | SkipJsonSchema[InstanceOf[Unconfigured]],
        Field(alias="nodeColors", default_factory=Unconfigured, exclude_if=Unconfigured().excludes),
    ]
