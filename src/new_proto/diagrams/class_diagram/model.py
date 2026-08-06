from enum import StrEnum

from new_proto.core import Annotation, Container, Diagram, Element, Entity, Occurrence, Relation


class Visibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    PACKAGE = "package"


class Member(Entity, Occurrence):
    def __init__(self, member_id: str, name: str, visibility: Visibility) -> None:
        Element.__init__(self)
        self._id = member_id
        self.name = name
        self.visibility = visibility

    @property
    def id(self) -> str:
        return self._id


class Attribute(Member):
    def __init__(self, member_id: str, name: str, type_name: str = "", visibility: Visibility = Visibility.PUBLIC) -> None:
        super().__init__(member_id, name, visibility)
        self.type_name = type_name

    @property
    def kind(self) -> str:
        return "attribute"


class Operation(Member):
    def __init__(
        self,
        member_id: str,
        name: str,
        parameters: tuple[str, ...] = (),
        return_type: str = "",
        visibility: Visibility = Visibility.PUBLIC,
    ) -> None:
        super().__init__(member_id, name, visibility)
        self.parameters = parameters
        self.return_type = return_type

    @property
    def kind(self) -> str:
        return "operation"


class Class(Entity, Container):
    def __init__(self, class_id: str, name: str) -> None:
        Element.__init__(self)
        self._id = class_id
        self.name = name
        self._init_container()

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> str:
        return "class"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, Member)

    def add_attribute(
        self, name: str, type_name: str = "", *, attribute_id: str | None = None, visibility: Visibility = Visibility.PUBLIC
    ) -> Attribute:
        attribute = Attribute(attribute_id or self.new_id("attribute"), name, type_name, visibility)
        self.add(attribute)
        return attribute

    def add_operation(
        self,
        name: str,
        parameters: tuple[str, ...] = (),
        return_type: str = "",
        *,
        operation_id: str | None = None,
        visibility: Visibility = Visibility.PUBLIC,
    ) -> Operation:
        operation = Operation(operation_id or self.new_id("operation"), name, parameters, return_type, visibility)
        self.add(operation)
        return operation

    def behaviours(self):
        from .behaviours import AddAttribute, AddOperation

        return (*super().behaviours(), AddAttribute(self), AddOperation(self))


class RelationshipKind(StrEnum):
    ASSOCIATION = "association"
    DEPENDENCY = "dependency"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"


class ClassRelationship(Entity, Relation):
    def __init__(
        self,
        relationship_id: str,
        source: str,
        target: str,
        relationship_kind: RelationshipKind,
        *,
        source_cardinality: str = "",
        target_cardinality: str = "",
        label: str = "",
    ) -> None:
        Element.__init__(self)
        self._id = relationship_id
        self.source = source
        self.target = target
        self.relationship_kind = relationship_kind
        self.source_cardinality = source_cardinality
        self.target_cardinality = target_cardinality
        self.label = label

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> str:
        return "class-relationship"

    @property
    def endpoints(self) -> tuple[str, ...]:
        return self.source, self.target


class Note(Entity, Annotation):
    def __init__(self, note_id: str, text: str, targets: tuple[str, ...] = ()) -> None:
        Element.__init__(self)
        self._id = note_id
        self.text = text
        self._targets = targets

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> str:
        return "note"

    @property
    def targets(self) -> tuple[str, ...]:
        return self._targets


class ClassDiagram(Diagram):
    @property
    def diagram_type(self) -> str:
        return "class-diagram"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, Class)

    def add_class(self, name: str, *, class_id: str | None = None) -> Class:
        class_ = Class(class_id or self.new_id("class"), name)
        self.add(class_)
        return class_

    def relate(
        self,
        source_id: str,
        target_id: str,
        kind: RelationshipKind,
        *,
        source_cardinality: str = "",
        target_cardinality: str = "",
        label: str = "",
    ) -> ClassRelationship:
        source = self.find(source_id)
        target = self.find(target_id)
        if not isinstance(source, Class) or not isinstance(target, Class):
            raise TypeError("Class relationships must connect classes")
        relationship = ClassRelationship(
            self.new_id("relationship"), source.id, target.id, kind,
            source_cardinality=source_cardinality,
            target_cardinality=target_cardinality,
            label=label,
        )
        self.add_relation(relationship)
        return relationship

    def add_note(self, text: str, *, targets: tuple[str, ...] = ()) -> Note:
        for target_id in targets:
            if not isinstance(self.find(target_id), Class):
                raise TypeError("Class-diagram notes can only annotate classes")
        note = Note(self.new_id("note"), text, targets)
        self.add_annotation(note)
        return note

    def behaviours(self):
        from .behaviours import AddClass, AddNote, RelateClasses

        return (*super().behaviours(), AddClass(self), RelateClasses(self), AddNote(self))
