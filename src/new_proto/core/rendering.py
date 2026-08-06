from typing import Protocol, TypeVar

SourceT = TypeVar("SourceT", contravariant=True)
ResultT = TypeVar("ResultT", covariant=True)


class Renderer(Protocol[SourceT, ResultT]):
    """Technology-neutral strategy for transforming a source into an output."""

    def render(self, source: SourceT) -> ResultT: ...


__all__ = ["Renderer"]
