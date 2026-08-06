from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Relation:
    """An identified binding between at least two diagram elements.

    The aggregate, rather than this value object, verifies cardinality and
    referential integrity against its current element state.
    """

    id: str
    element_ids: tuple[str, ...]
    label: str = ""
