from abc import ABC, abstractmethod


class Element(ABC):
    @property
    @abstractmethod
    def kind(self) -> str:
        pass
