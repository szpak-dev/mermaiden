from collections.abc import Iterator, Mapping
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Protocol, cast

from jsonschema import Draft201909Validator
from jsonschema.exceptions import ValidationError
from yaml import safe_load


@dataclass(frozen=True, slots=True)
class ConfigurationViolation:
    path: str
    message: str


class SchemaValidator(Protocol):
    def iter_errors(self, instance: Any) -> Iterator[ValidationError]: ...


@dataclass(frozen=True, slots=True)
class MermaidConfiguration:
    schema: Mapping[str, Any]

    def validate(self, source: str) -> tuple[ConfigurationViolation, ...]:
        config = self.extract(source)
        validator = cast(SchemaValidator, Draft201909Validator(self._partial_schema()))
        errors = tuple(validator.iter_errors(config))
        return tuple(
            ConfigurationViolation(".".join(str(segment) for segment in error.absolute_path), error.message)
            for error in sorted(errors, key=lambda error: list(error.absolute_path))
        )

    @staticmethod
    def extract(source: str) -> Mapping[str, Any]:
        if not source.startswith("---\n"):
            return {}
        _, frontmatter, _ = source.split("---\n", 2)
        payload: object = safe_load(frontmatter)
        if not isinstance(payload, Mapping):
            raise ValueError("Mermaid frontmatter must be a mapping.")
        config: object = cast(Mapping[str, object], payload).get("config", {})
        if not isinstance(config, Mapping):
            raise ValueError("Mermaid frontmatter config must be a mapping.")
        return cast(Mapping[str, Any], config)

    def supports(self, config_key: str, schema_definition: str) -> bool:
        properties = cast(Mapping[str, Any], self.schema["properties"])
        definitions = cast(Mapping[str, Any], self.schema["$defs"])
        expected = {"$ref": f"#/$defs/{schema_definition}"}
        return properties.get(config_key) == expected and schema_definition in definitions

    def _partial_schema(self) -> dict[str, Any]:
        schema = deepcopy(dict(self.schema))
        self._remove_required(schema)
        return schema

    @classmethod
    def _remove_required(cls, value: Any) -> None:
        if isinstance(value, dict):
            mapping = cast(dict[str, Any], value)
            mapping.pop("required", None)
            for child in mapping.values():
                cls._remove_required(child)
        if isinstance(value, list):
            items = cast(list[Any], value)
            for child in items:
                cls._remove_required(child)
