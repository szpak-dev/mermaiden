from new_proto.interface import Interface


class Annotatable(Interface):
    """Marks a type that deliberately permits annotations to target its instances."""

    pass


class Annotation(Interface):
    """Optional meaning that refers to explicitly annotatable targets without mutating them."""

    @Interface.prop
    def targets(self) -> tuple[Annotatable, ...]: ...
