from dataclasses import dataclass
from typing import ClassVar

from ...core.annotation import Annotation


@dataclass(frozen=True, slots=True)
class Note(Annotation):
    kind: ClassVar[str] = "note"
    text: str
