from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Relation:
    id: str
    element_ids: tuple[str, ...]
    label: str = ""
