from ...core.domain import Relation


class StateTransition(Relation):
    scope_id: str = ""
    source_terminal: bool = False
    target_terminal: bool = False
