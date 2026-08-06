from new_proto.interface import Interface


class Annotatable(Interface):
    pass


class Annotation(Interface):
    @Interface.method
    def targets(self) -> tuple[Annotatable, ...]: ...
