import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from pydantic import RootModel

from mermaiden import Application
from mermaiden.core.domain import CommandPayload

from ._specialized import build_gitgraph_fixture
from .catalog import FixtureCatalog


class SchemaMapping(RootModel[dict[str, object]]):
    pass


class ObjectSequence(RootModel[list[object]]):
    pass


@dataclass(frozen=True, slots=True)
class ConfigurationProbe:
    diagram_id: str
    field: str
    value: object

    @property
    def id(self) -> str:
        return f"{self.diagram_id}.{self.field}"


@dataclass(frozen=True, slots=True)
class ConfigurationProof:
    diagram_id: str
    source: str
    configuration: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class RenderedConfigurationProbe:
    probe: ConfigurationProbe
    source: str

    @property
    def id(self) -> str:
        return self.probe.id


@dataclass(frozen=True, slots=True)
class ConfigurationProofCatalog:
    application: Application

    def proofs(self) -> tuple[ConfigurationProof, ...]:
        proofs: list[ConfigurationProof] = []
        for fixture in FixtureCatalog(self.application).fixtures():
            diagram_id = fixture.id
            payload = self.application.command_payload(diagram_id, "configure")
            configuration = self.complete_configuration(payload)
            self.application.execute(fixture.diagram, "configure", configuration)
            proofs.append(
                ConfigurationProof(
                    diagram_id,
                    self.application.render(fixture.diagram),
                    configuration,
                )
            )
        return tuple(sorted(proofs, key=lambda proof: proof.diagram_id))

    def probes(self) -> tuple[ConfigurationProbe, ...]:
        probes: list[ConfigurationProbe] = []
        for info in self.application.available_diagrams():
            payload = self.application.command_payload(info.id, "configure")
            schema = payload.schema()
            properties = self.mapping(schema.get("properties"), f"{info.id} configuration properties")
            defaults = payload.validate({}).values
            for field, raw_node in properties.items():
                node = self.mapping(raw_node, f"{info.id}.{field} schema")
                candidates = self.candidates(field, self.resolve(schema, node), defaults.get(field))
                validated: list[object] = []
                for candidate in candidates:
                    try:
                        value = payload.validate({field: candidate}).values[field]
                    except (KeyError, ValueError):
                        continue
                    if value not in validated:
                        validated.append(value)
                if not validated:
                    raise ValueError(f"No valid configuration probe for '{info.id}.{field}'.")
                probes.extend(ConfigurationProbe(info.id, field, value) for value in validated)
        return tuple(probes)

    def rendered_probes(self) -> tuple[RenderedConfigurationProbe, ...]:
        snapshots = {
            fixture.id: self.application.snapshot(fixture.diagram).to_dict()
            for fixture in FixtureCatalog(self.application).fixtures()
        }
        rendered: list[RenderedConfigurationProbe] = []
        for probe in self.probes():
            if probe.diagram_id == "gitGraph" and probe.field == "mainBranchName":
                if not isinstance(probe.value, str):
                    raise ValueError("GitGraph mainBranchName probe must be text.")
                diagram = build_gitgraph_fixture(self.application, probe.value)
            else:
                diagram = self.application.restore(snapshots[probe.diagram_id])
            self.application.execute(diagram, "configure", {probe.field: probe.value})
            snapshot = self.application.snapshot(diagram).to_dict()
            source = self.application.render(diagram)
            if self.application.render(self.application.restore(snapshot)) != source:
                raise ValueError(f"Configuration probe '{probe.id}' changed after snapshot restoration.")
            rendered.append(RenderedConfigurationProbe(probe, source))
        return tuple(rendered)

    def complete_configuration(self, payload: CommandPayload) -> Mapping[str, object]:
        schema = payload.schema()
        properties = self.mapping(schema.get("properties"), "configuration properties")
        values = dict(payload.validate({}).values)
        for field, raw_node in properties.items():
            if field in values:
                continue
            node = self.mapping(raw_node, f"{field} schema")
            candidates = self.candidates(field, self.resolve(schema, node), None)
            for candidate in candidates:
                try:
                    values[field] = payload.validate({field: candidate}).values[field]
                except (KeyError, ValueError):
                    continue
                break
            else:
                raise ValueError(f"No explicit configuration value for '{field}'.")
        validated = payload.validate(values).values
        if set(validated) != set(properties):
            missing = ", ".join(sorted(set(properties) - set(validated)))
            raise ValueError(f"Configuration proof is missing fields: {missing}")
        return validated

    def candidates(self, field: str, node: Mapping[str, object], default: object) -> tuple[object, ...]:
        enum = node.get("enum")
        if enum is not None:
            return self.sequence(enum, f"{field} enum")
        alternatives = node.get("anyOf")
        if alternatives is not None:
            values: list[object] = []
            for alternative in self.sequence(alternatives, f"{field} alternatives"):
                resolved = self.mapping(alternative, f"{field} alternative")
                values.extend(self.candidates(field, resolved, default))
            return tuple(values)
        kind = node.get("type")
        if kind == "boolean":
            return (False, True)
        if kind == "integer":
            return self.numeric_candidates(node, default, integral=True)
        if kind == "number":
            return self.numeric_candidates(node, default, integral=False)
        if kind == "string":
            return self.string_candidates(field, default)
        if kind == "array":
            item = self.mapping(node.get("items"), f"{field} items")
            sample = self.candidates(field, item, None)[-1]
            return ([], [sample], [sample, sample])
        if kind == "object":
            properties = node.get("properties")
            property_schemas: Mapping[str, object]
            try:
                property_schemas = self.mapping(properties, f"{field} properties")
            except ValueError:
                property_schemas = dict[str, object]()
            if property_schemas:
                complete: dict[str, object] = {
                    name: self.candidates(
                        name,
                        self.resolve(node, self.mapping(child, f"{field}.{name} schema")),
                        None,
                    )[-1]
                    for name, child in property_schemas.items()
                }
                return (dict[str, object](), complete)
            additional = node.get("additionalProperties")
            additional_schema: Mapping[str, object]
            try:
                additional_schema = self.mapping(additional, f"{field} values")
            except ValueError:
                additional_schema = dict[str, object]()
            if additional_schema:
                value = self.candidates(field, additional_schema, None)[-1]
                return (dict[str, object](), {"proof": value, "second": value})
            return (dict[str, object](),)
        if default is not None:
            return (default,)
        raise ValueError(f"Unsupported configuration schema for '{field}': {node}")

    def numeric_candidates(
        self,
        node: Mapping[str, object],
        default: object,
        *,
        integral: bool,
    ) -> tuple[object, ...]:
        minimum = node.get("minimum", node.get("exclusiveMinimum"))
        maximum = node.get("maximum", node.get("exclusiveMaximum"))
        step = 1 if integral else 0.25
        lower = minimum if isinstance(minimum, int | float) else -1
        upper = maximum if isinstance(maximum, int | float) else 1
        if isinstance(minimum, int | float) and "exclusiveMinimum" in node:
            lower += step
        if isinstance(maximum, int | float) and "exclusiveMaximum" in node:
            upper -= step
        values: list[object] = [lower]
        if lower <= 0 <= upper:
            values.append(0)
        if isinstance(minimum, int | float) and isinstance(maximum, int | float):
            values.append(lower + (upper - lower) / 2)
        values.append(upper)
        if integral:
            values = [round(value) if isinstance(value, int | float) else value for value in values]
        if isinstance(default, int | float) and default not in values:
            values.append(default)
        return tuple(dict.fromkeys(values))

    def string_candidates(self, field: str, default: object) -> tuple[object, ...]:
        lowered = field.lower()
        if "color" in lowered or "fill" in lowered or "stroke" in lowered:
            values: list[object] = ["#2F80ED", "#F2994A"]
        elif "fontfamily" in lowered:
            values = ["Arial", "monospace"]
        elif "fontweight" in lowered:
            values = ["400", "700"]
        elif "fontsize" in lowered:
            values = ["12", "0.5"]
        elif field == "axisFormat":
            values = ["%Y-%m-%d", "%d %b"]
        elif field == "tickInterval":
            values = ["1day", "1week"]
        elif field == "ticketBaseUrl":
            values = ["", "https://example.test/tickets/"]
        elif field == "mainBranchName":
            values = ["main", "trunk"]
        elif field == "seed":
            values = ["7", "proof-seed"]
        else:
            values = ["", "proof"]
        if isinstance(default, str) and default not in values:
            values.append(default)
        return tuple(values)

    def resolve(self, root: Mapping[str, object], node: Mapping[str, object]) -> Mapping[str, object]:
        reference = node.get("$ref")
        if not isinstance(reference, str):
            return node
        resolved: object = root
        for part in reference.removeprefix("#/").split("/"):
            resolved = self.mapping(resolved, reference).get(part)
        return self.resolve(root, self.mapping(resolved, reference))

    def mapping(self, value: object, description: str) -> Mapping[str, object]:
        try:
            return SchemaMapping.model_validate(value).root
        except ValueError as error:
            raise ValueError(f"Expected {description} to be a mapping.") from error

    def sequence(self, value: object, description: str) -> tuple[object, ...]:
        try:
            return tuple(ObjectSequence.model_validate(value).root)
        except ValueError as error:
            raise ValueError(f"Expected {description} to be a sequence.") from error


@dataclass(frozen=True, slots=True)
class ConfigurationProofRenderer:
    mermaid_version: str
    timeout_seconds: int = 180
    batch_size: int = 80

    def render(self, sources: Mapping[str, str]) -> Mapping[str, str]:
        version = subprocess.run(("mmdc", "--version"), capture_output=True, check=False, text=True, timeout=60)
        observed = version.stdout.strip()
        if version.returncode or observed != self.mermaid_version:
            raise RuntimeError(
                f"Expected mmdc {self.mermaid_version}, observed {observed or version.stderr.strip()}."
            )
        items = tuple(sources.items())
        rendered: dict[str, str] = {}
        for start in range(0, len(items), self.batch_size):
            batch = items[start : start + self.batch_size]
            rendered.update(self.render_batch(batch))
        return rendered

    def render_batch(self, sources: Sequence[tuple[str, str]]) -> Mapping[str, str]:
        with tempfile.TemporaryDirectory(prefix="mermaiden-configuration-proofs-") as temporary:
            directory = Path(temporary)
            input_path = directory / "proofs.md"
            output_path = directory / "proofs.rendered.md"
            input_path.write_text(
                "\n".join(f"## {diagram_id}\n```mermaid\n{source}```" for diagram_id, source in sources),
                encoding="utf-8",
            )
            process = subprocess.run(
                ("mmdc", "-i", str(input_path), "-o", str(output_path)),
                capture_output=True,
                check=False,
                text=True,
                timeout=self.timeout_seconds,
            )
            if process.returncode:
                if len(sources) > 1:
                    midpoint = len(sources) // 2
                    return {
                        **self.render_batch(sources[:midpoint]),
                        **self.render_batch(sources[midpoint:]),
                    }
                diagram_id = sources[0][0]
                details = process.stderr.strip() or process.stdout.strip()
                raise RuntimeError(f"Mermaid failed to render '{diagram_id}': {details}")
            rendered: dict[str, str] = {}
            for index, (diagram_id, _source) in enumerate(sources, start=1):
                path = directory / f"proofs.rendered-{index}.svg"
                if not path.exists():
                    raise RuntimeError(f"Mermaid did not create SVG proof '{diagram_id}'.")
                svg = path.read_text(encoding="utf-8")
                document = ElementTree.fromstring(svg)
                if any(
                    {"error-icon", "error-text"}.intersection(element.attrib.get("class", "").split())
                    for element in document.iter()
                ) or any(
                    message in svg
                    for message in ("Syntax error in text", "Maximum text size in diagram exceeded")
                ):
                    raise RuntimeError(f"Mermaid created an error SVG for '{diagram_id}'.")
                if any(token in svg for token in ("NaN", "Infinity")):
                    raise RuntimeError(f"Mermaid created invalid geometry for '{diagram_id}'.")
                rendered[diagram_id] = svg
            return rendered
