from typing import Annotated

from pydantic import Field

from ..domain import (
    MermaidDiagramConfiguration,
    MermaidLook,
    MermaidLookField,
    MermaidTheme,
    MermaidThemeField,
    OmittableLook,
    OmittableTheme,
)


class VennConfiguration(MermaidDiagramConfiguration):
    theme: MermaidThemeField = OmittableTheme(root=MermaidTheme.REDUX_COLOR)
    look: MermaidLookField = OmittableLook(root=MermaidLook.NEO)
    width: Annotated[float, Field(alias="width", ge=1)] = 800
    height: Annotated[float, Field(alias="height", ge=1)] = 450
    padding: Annotated[float, Field(alias="padding", ge=0)] = 8
    use_debug_layout: Annotated[bool, Field(alias="useDebugLayout")] = False
