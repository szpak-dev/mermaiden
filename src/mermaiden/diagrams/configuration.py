from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict


class MermaidConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    wrap: bool = True
    diagrams: Mapping[str, "MermaidDiagramConfiguration"]

    def to_mermaid(self) -> dict[str, object]:
        return {
            "wrap": self.wrap,
            **{source: configuration.to_mermaid() for source, configuration in self.diagrams.items()},
        }


class MermaidDiagramConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    def document(self, source: str) -> MermaidConfiguration:
        return MermaidConfiguration(diagrams={source: self})

    def to_mermaid(self) -> dict[str, object]:
        return self.model_dump(mode="json", by_alias=True)
