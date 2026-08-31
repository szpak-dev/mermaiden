from collections.abc import Mapping

from ...core.domain import ValueModel


class DiagramDescription(ValueModel):
    id: str
    name: str
    elements: Mapping[str, Mapping[str, object]]
    relations: Mapping[str, Mapping[str, object]]
    annotations: Mapping[str, Mapping[str, object]]
    commands: Mapping[str, Mapping[str, object]]
