from abc import ABC, abstractmethod

class Behaviour(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, **arguments: object) -> object:
        pass


class RemoveChild(Behaviour):
    pass


class MoveChild(Behaviour):
    pass


class RemoveRelation(Behaviour):
    pass


class RemoveAnnotation(Behaviour):
    pass
