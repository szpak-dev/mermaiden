from dataclasses import dataclass

from wireup import injectable

from ...diagrams.application import DiagramsApplication
from ..application import MermaidApplication
from ..fixtures import DiagramFixtures
from .configuration import ConfigurationViolation, DiagramConfigurationContract, MermaidConfiguration
from .parser import MermaidSyntaxValidator, MermaidSyntaxViolation
from .schema import MermaidSchemaLock, MermaidSchemaStore


@dataclass(frozen=True, slots=True)
class DiagramCompatibility:
    diagram_id: str
    configuration: DiagramConfigurationContract
    violations: tuple[ConfigurationViolation, ...]
    schema_supported: bool

    @property
    def config_key(self) -> str:
        return self.configuration.config_key

    @property
    def schema_definition(self) -> str:
        return self.configuration.schema_definition

    @property
    def valid(self) -> bool:
        return self.schema_supported and not self.violations


@dataclass(frozen=True, slots=True)
class MissingDiagramCompatibility:
    config_key: str
    schema_definition: str


@dataclass(frozen=True, slots=True)
class CompatibilityReport:
    lock: MermaidSchemaLock
    diagrams: tuple[DiagramCompatibility, ...]
    missing_diagrams: tuple[MissingDiagramCompatibility, ...]
    syntax_violations: tuple[MermaidSyntaxViolation, ...] = ()

    @property
    def valid(self) -> bool:
        return (
            all(diagram.valid for diagram in self.diagrams)
            and not self.missing_diagrams
            and not self.syntax_violations
        )

    def diagram_valid(self, diagram: DiagramCompatibility) -> bool:
        return diagram.valid and all(violation.diagram_id != diagram.diagram_id for violation in self.syntax_violations)


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class MermaidCompatibilityService:
    fixtures: DiagramFixtures
    syntax: MermaidSyntaxValidator
    registry: DiagramsApplication
    renderer: MermaidApplication
    schemas: MermaidSchemaStore

    def inspect(self) -> CompatibilityReport:
        return self._inspect(False)

    def verify(self) -> CompatibilityReport:
        return self._inspect(True)

    def _inspect(self, verify_syntax: bool) -> CompatibilityReport:
        lock = self.schemas.lock()
        configuration = MermaidConfiguration(self.schemas.load())
        diagrams: list[DiagramCompatibility] = []
        missing: list[MissingDiagramCompatibility] = []
        fixture_sources = self.fixtures.render_compatibility_sources() if verify_syntax else {}
        sources: dict[str, str] = {}
        for upstream in self.schemas.diagram_configs():
            try:
                info = self.registry.get_by_config_key(upstream.config_key)
            except KeyError:
                missing.append(MissingDiagramCompatibility(
                    upstream.config_key, upstream.schema_definition))
                continue
            source = self.renderer.render(self.registry.get_diagram(info.id))
            local = configuration.local_contract(
                info.config_key, info.schema_definition, source)
            sources[info.id] = fixture_sources[info.id] if verify_syntax and info.id in fixture_sources else source
            diagrams.append(
                DiagramCompatibility(
                    info.id,
                    local,
                    configuration.validate(local),
                    configuration.supports(local, upstream),
                )
            )
        syntax_violations = self.syntax.validate(
            sources) if verify_syntax else ()
        return CompatibilityReport(lock, tuple(diagrams), tuple(missing), syntax_violations)
