from dataclasses import dataclass

from ...core.annotation import Annotation, TargetKind, TargetRef


@dataclass(frozen=True, slots=True)
class Note(Annotation):
    annotation_id: str
    text: str
    target_id: str
    target_kind: TargetKind = TargetKind.ELEMENT

    @property
    def id(self) -> str:
        return self.annotation_id

    @property
    def targets(self) -> tuple[TargetRef, ...]:
        return (TargetRef(self.target_kind, self.target_id),)
