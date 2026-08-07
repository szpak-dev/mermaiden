from dataclasses import dataclass
from typing import ClassVar

from ...core.annotation import Annotation


@dataclass(frozen=True, slots=True)
class TreeAnnotation(Annotation):
    kind: ClassVar[str] = "tree_annotation"
    highlight: bool = False
    icon: str = ""
    description: str = ""
