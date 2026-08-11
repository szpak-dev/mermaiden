from .model import ClassifiedValueModel


class Relation(ClassifiedValueModel):
    id: str
    element_ids: tuple[str, ...]
    label: str = ""

    @property
    def source_id(self) -> str:
        return self.element_ids[0] if self.element_ids else ""

    @property
    def target_id(self) -> str:
        return self.element_ids[1] if len(self.element_ids) > 1 else ""


class ConditionalRelation(Relation):
    @property
    def condition(self) -> str:
        return self.label
