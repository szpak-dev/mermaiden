from dataclasses import dataclass

from wireup import injectable

from ...diagrams.registry import DiagramRegistry
from ..service import MermaidRenderer
from .configuration import ConfigurationViolation, MermaidConfiguration
from .parser import MermaidSyntaxValidator, MermaidSyntaxViolation
from .schema import MermaidSchemaLock, MermaidSchemaStore


@dataclass(frozen=True, slots=True)
class DiagramCompatibility:
    diagram_id: str
    config_key: str
    schema_definition: str
    violations: tuple[ConfigurationViolation, ...]
    schema_supported: bool

    @property
    def valid(self) -> bool:
        return self.schema_supported and not self.violations


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    lock: MermaidSchemaLock
    diagrams: tuple[DiagramCompatibility, ...]
    syntax_violations: tuple[MermaidSyntaxViolation, ...] = ()

    @property
    def valid(self) -> bool:
        return all(diagram.valid for diagram in self.diagrams) and not self.syntax_violations


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class MermaidCompatibility:
    syntax: MermaidSyntaxValidator
    registry: DiagramRegistry
    renderer: MermaidRenderer
    schemas: MermaidSchemaStore

    def inspect(self) -> CompatibilityReport:
        return self._inspect(())

    def verify(self) -> CompatibilityReport:
        return self._inspect(())

    def _inspect(self, syntax_violations: tuple[MermaidSyntaxViolation, ...]) -> CompatibilityReport:
        lock = self.schemas.lock()
        configuration = MermaidConfiguration(self.schemas.load())
        diagrams = tuple(
            DiagramCompatibility(
                info.id,
                info.config_key,
                info.schema_definition,
                configuration.validate(self.renderer.render(info.diagram)),
                configuration.supports(info.config_key, info.schema_definition),
            )
            for info in self.registry
        )
        return CompatibilityReport(lock, diagrams, syntax_violations)
