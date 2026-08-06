from dataclasses import dataclass

from ...core.annotation import Annotation


@dataclass(frozen=True, slots=True)
class Note(Annotation):
    pass
