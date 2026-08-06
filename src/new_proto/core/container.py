from abc import abstractmethod

from .base import Element


class Container(Element):
    @property
    @abstractmethod
    def elements(self) -> tuple[Element, ...]:
        pass

    @abstractmethod
    def accepts(self, element: Element) -> bool:
        pass

    def add(self, element: Element, *, after_id: str | None = None) -> None:
        pass

    def remove(self, element_id: str) -> Element:
        pass

    def move(self, element_id: str, *, after_id: str | None = None) -> None:
        pass
