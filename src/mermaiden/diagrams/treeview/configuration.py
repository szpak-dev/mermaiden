from collections.abc import Mapping
from typing import Annotated

from pydantic import ConfigDict, Field, RootModel

from ...core.characters import OptionalText, Text
from ..domain import MermaidDiagramConfiguration


class TreeViewIconMap(
    RootModel[Mapping[str, Annotated[str, Field(pattern=Text.pattern, description=Text.description)]]]
):
    model_config = ConfigDict(frozen=True)


class TreeViewDiagramConfiguration(MermaidDiagramConfiguration):
    row_indent: Annotated[float, Field(alias="rowIndent", ge=0)] = 10
    padding_x: Annotated[float, Field(alias="paddingX", ge=0)] = 5
    padding_y: Annotated[float, Field(alias="paddingY", ge=0)] = 5
    line_thickness: Annotated[float, Field(alias="lineThickness", ge=0)] = 1
    show_icons: Annotated[bool, Field(alias="showIcons")] = False
    default_icon_pack: Annotated[
        str, Field(alias="defaultIconPack", pattern=OptionalText.pattern, description=OptionalText.description)
    ] = ""
    filename_icons: Annotated[TreeViewIconMap, Field(alias="filenameIcons")] = TreeViewIconMap(root={})
    extension_icons: Annotated[TreeViewIconMap, Field(alias="extensionIcons")] = TreeViewIconMap(root={})
