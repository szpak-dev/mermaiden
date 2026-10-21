from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidDiagramConfiguration


class MindmapColorBy(StrEnum):
    BRANCH = "branch"
    DEPTH = "depth"


class MindmapDiagramConfiguration(MermaidDiagramConfiguration):
    color_by: Annotated[MindmapColorBy, Field(alias="colorBy")] = MindmapColorBy.BRANCH
    padding: Annotated[float, Field(alias="padding")] = 10
    max_node_width: Annotated[float, Field(alias="maxNodeWidth")] = 200
    layout_algorithm: Annotated[
        str, Field(alias="layoutAlgorithm", pattern=Text.pattern, description=Text.description)
    ] = "cose-bilkent"
