from new_proto.core import Behaviour

from .model import Class, ClassDiagram, RelationshipKind, Visibility


class AddClass(Behaviour):
    name = "add_class"

    def execute(self, *, name: str, class_id: str | None = None):
        assert isinstance(self.owner, ClassDiagram)
        return self.owner.add_class(name, class_id=class_id)


class AddAttribute(Behaviour):
    name = "add_attribute"

    def execute(
        self, *, name: str, type_name: str = "", attribute_id: str | None = None, visibility: Visibility = Visibility.PUBLIC
    ):
        assert isinstance(self.owner, Class)
        return self.owner.add_attribute(name, type_name, attribute_id=attribute_id, visibility=visibility)


class AddOperation(Behaviour):
    name = "add_operation"

    def execute(
        self,
        *,
        name: str,
        parameters: tuple[str, ...] = (),
        return_type: str = "",
        operation_id: str | None = None,
        visibility: Visibility = Visibility.PUBLIC,
    ):
        assert isinstance(self.owner, Class)
        return self.owner.add_operation(
            name, parameters, return_type, operation_id=operation_id, visibility=visibility
        )


class RelateClasses(Behaviour):
    name = "relate_classes"

    def execute(
        self,
        *,
        source_id: str,
        target_id: str,
        kind: RelationshipKind,
        source_cardinality: str = "",
        target_cardinality: str = "",
        label: str = "",
    ):
        assert isinstance(self.owner, ClassDiagram)
        return self.owner.relate(
            source_id,
            target_id,
            kind,
            source_cardinality=source_cardinality,
            target_cardinality=target_cardinality,
            label=label,
        )


class AddNote(Behaviour):
    name = "add_note"

    def execute(self, *, text: str, targets: tuple[str, ...] = ()):
        assert isinstance(self.owner, ClassDiagram)
        return self.owner.add_note(text, targets=targets)
