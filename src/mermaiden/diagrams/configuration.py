from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, SerializeAsAny


class MermaidConfigurationNaming:
    @staticmethod
    def to_camel_case(value: str) -> str:
        first, *remaining = value.split("_")
        return first + "".join(word.capitalize() for word in remaining)


class MermaidConfigurationModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=MermaidConfigurationNaming.to_camel_case,
        frozen=True,
        populate_by_name=True,
    )


class MermaidConfiguration(MermaidConfigurationModel):

    wrap: bool = True
    diagrams: Mapping[str, SerializeAsAny["MermaidDiagramConfiguration"]]

    def to_mermaid(self) -> dict[str, object]:
        document = self.model_dump(mode="json", by_alias=True)
        diagrams = document.pop("diagrams")
        return {**document, **diagrams}


class MermaidDiagramConfiguration(MermaidConfigurationModel):

    def document(self, source: str) -> MermaidConfiguration:
        return MermaidConfiguration(diagrams={source: self})
