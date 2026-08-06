from abc import ABC, abstractmethod


class Element(ABC):
    """A diagram member with an identity local to its diagram."""

    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    def owner_id(self) -> str | None:
        """ID of the containing element, when the element is nested."""

        return None


class Container(Element, ABC):
    """Marker for an element that may own other elements."""

