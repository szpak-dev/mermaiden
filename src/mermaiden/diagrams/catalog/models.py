from collections.abc import Mapping

from ...core.domain import ValueModel


class ElementPlacement(ValueModel):
    allowed_parents: tuple[str, ...]


class DiagramDescription(ValueModel):
    id: str
    name: str
    elements: Mapping[str, Mapping[str, object]]
    relations: Mapping[str, Mapping[str, object]]
    annotations: Mapping[str, Mapping[str, object]]
    placements: Mapping[str, ElementPlacement]
    commands: Mapping[str, Mapping[str, object]]
