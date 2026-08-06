from new_proto.interface import Interface


class Annotatable(Interface):
    """Marks a type that may deliberately be targeted by an annotation."""

    pass


class Annotation(Interface):
    """Optional meaning attached only to explicitly annotatable diagram targets."""

    @Interface.prop
    def targets(self) -> tuple[Annotatable, ...]: ...
