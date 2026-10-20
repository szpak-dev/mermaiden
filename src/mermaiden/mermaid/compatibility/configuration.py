from collections.abc import Mapping
from dataclasses import dataclass

from jsonschema import Draft201909Validator
from pydantic import BaseModel, ConfigDict, Field, RootModel
from yaml import safe_load

from ..schema import MermaidConfigurationOverride, MermaidDiagramConfig


@dataclass(frozen=True, slots=True)
class ConfigurationViolation:
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class DiagramConfigurationContract:
    config_key: str
    schema_definition: str
    values: Mapping[str, object]


class ConfigurationSchemaMapping(RootModel[Mapping[str, object]]):
    model_config = ConfigDict(frozen=True)

    def include(self, name: str, children: dict[str, Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
        return {**children, name: self.root}

    @property
    def allows_additional_properties(self) -> bool:
        return False


class ConfigurationSchemaMappings(RootModel[tuple[ConfigurationSchemaMapping, ...]]):
    model_config = ConfigDict(frozen=True)


class ConfigurationSchemaProperties(RootModel[Mapping[str, ConfigurationSchemaMapping]]):
    model_config = ConfigDict(frozen=True)


class ConfigurationSchemaStrings(RootModel[tuple[str, ...]]):
    model_config = ConfigDict(frozen=True)


class ConfigurationSchemaSingleType(RootModel[str]):
    model_config = ConfigDict(frozen=True, strict=True)

    @property
    def values(self) -> tuple[str, ...]:
        return (self.root,)


class ConfigurationSchemaMultipleTypes(RootModel[tuple[str, ...]]):
    model_config = ConfigDict(frozen=True)

    @property
    def values(self) -> tuple[str, ...]:
        return self.root


class ConfigurationSchemaAbsentType(RootModel[None]):
    model_config = ConfigDict(frozen=True, strict=True)

    @property
    def values(self) -> tuple[str, ...]:
        return ()


class ConfigurationSchemaTypes(RootModel[object]):
    model_config = ConfigDict(frozen=True, strict=True)

    root: Annotated[
        ConfigurationSchemaSingleType | ConfigurationSchemaMultipleTypes | ConfigurationSchemaAbsentType,
        Field(union_mode="left_to_right"),
    ]

    @property
    def values(self) -> tuple[str, ...]:
        return self.root.values


class ConfigurationSchemaEnumerationValues(RootModel[tuple[object, ...]]):
    model_config = ConfigDict(frozen=True)

    @property
    def values(self) -> tuple[object, ...] | None:
        return self.root


class ConfigurationSchemaEnumerationAbsent(RootModel[None]):
    model_config = ConfigDict(frozen=True, strict=True)

    @property
    def values(self) -> tuple[object, ...] | None:
        return None


class ConfigurationSchemaEnumeration(RootModel[object]):
    model_config = ConfigDict(frozen=True, strict=True)

    root: Annotated[
        ConfigurationSchemaEnumerationValues | ConfigurationSchemaEnumerationAbsent,
        Field(union_mode="left_to_right"),
    ]

    @property
    def values(self) -> tuple[object, ...] | None:
        return self.root.values


class ConfigurationSchemaNodeMapping(RootModel[Mapping[str, "ConfigurationSchemaNode"]]):
    model_config = ConfigDict(frozen=True, strict=True)

    def without_required(self) -> object:
        return {
            key: child.without_required()
            for key, child in self.root.items()
            if key != "required"
        }


class ConfigurationSchemaNodeSequence(RootModel[tuple["ConfigurationSchemaNode", ...]]):
    model_config = ConfigDict(frozen=True)

    def without_required(self) -> object:
        return [child.without_required() for child in self.root]


class ConfigurationSchemaNodeScalar(RootModel[None | bool | int | float | str]):
    model_config = ConfigDict(frozen=True, strict=True)

    def without_required(self) -> object:
        return self.root


class ConfigurationSchemaNode(RootModel[object]):
    model_config = ConfigDict(frozen=True, strict=True)

    root: Annotated[
        ConfigurationSchemaNodeMapping | ConfigurationSchemaNodeSequence | ConfigurationSchemaNodeScalar,
        Field(union_mode="left_to_right"),
    ]

    def without_required(self) -> object:
        return self.root.without_required()


class ConfigurationSchemaReference(RootModel[str | None]):
    model_config = ConfigDict(frozen=True)

    @property
    def internal(self) -> bool:
        return self.root is not None and self.root.startswith("#/")

    @property
    def segments(self) -> tuple[str, ...]:
        if self.root is None:
            return ()
        return tuple(
            segment.replace("~1", "/").replace("~0", "~")
            for segment in self.root.removeprefix("#/").split("/")
        )


class ConfigurationSchemaDocument(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)

    properties: Mapping[str, ConfigurationSchemaMapping]
    definitions: Mapping[str, ConfigurationSchemaMapping] = Field(alias="$defs")


@dataclass(frozen=True, slots=True)
class ConfigurationSchemaAlternativeFacet:
    schema_type: "ConfigurationSchemaFacet"
    constraint: "ConfigurationSchemaFacet"


@dataclass(frozen=True, slots=True)
class ConfigurationSchemaFacet:
    present: bool
    value: object
    alternatives: tuple[ConfigurationSchemaAlternativeFacet, ...] = ()


class ConfigurationSchemaBoolean(RootModel[bool]):
    model_config = ConfigDict(frozen=True)

    def include(self, name: str, children: dict[str, Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
        return children

    @property
    def allows_additional_properties(self) -> bool:
        return self.root


class ConfigurationSchemaAbsent(RootModel[None]):
    model_config = ConfigDict(frozen=True, strict=True)

    def include(self, name: str, children: dict[str, Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
        return children

    @property
    def allows_additional_properties(self) -> bool:
        return False


class ConfigurationSchemaChild(RootModel[object]):
    model_config = ConfigDict(frozen=True, strict=True)

    root: Annotated[
        ConfigurationSchemaMapping | ConfigurationSchemaBoolean | ConfigurationSchemaAbsent,
        Field(union_mode="left_to_right"),
    ] = Field(default_factory=ConfigurationSchemaAbsent)

    def include(self, name: str, children: dict[str, Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
        return self.root.include(name, children)

    @property
    def allows_additional_properties(self) -> bool:
        return self.root.allows_additional_properties


class ConfigurationSchemaContainer(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True, populate_by_name=True)

    properties: Mapping[str, ConfigurationSchemaMapping] = Field(default_factory=dict)
    items: ConfigurationSchemaChild = Field(default_factory=ConfigurationSchemaChild)
    additional_properties: ConfigurationSchemaChild = Field(
        default_factory=ConfigurationSchemaChild,
        alias="additionalProperties",
    )

    def children(self) -> dict[str, Mapping[str, object]]:
        children = {name: child.root for name, child in self.properties.items()}
        children = self.items.include("items", children)
        return self.additional_properties.include("additionalProperties", children)

    @property
    def allows_additional_properties(self) -> bool:
        return self.additional_properties.allows_additional_properties


@dataclass(frozen=True, slots=True)
class MermaidConfiguration:
    schema: Mapping[str, object]
    overrides: Mapping[str, MermaidConfigurationOverride]

    facets = (
        "type",
        "nullability",
        "enum",
        "default",
        "minimum",
        "exclusiveMinimum",
        "maximum",
        "exclusiveMaximum",
        "multipleOf",
        "uniqueItems",
    )

    def local_contract(
        self,
        config_key: str,
        schema_definition: str,
        source: str,
    ) -> DiagramConfigurationContract:
        return DiagramConfigurationContract(config_key, schema_definition, self.extract(source))

    def validate(self, contract: DiagramConfigurationContract) -> tuple[ConfigurationViolation, ...]:
        validator = Draft201909Validator(self.partial_schema())
        errors = tuple(validator.iter_errors(contract.values))
        return tuple(
            ConfigurationViolation(".".join(str(segment) for segment in error.absolute_path), error.message)
            for error in sorted(errors, key=lambda error: list(error.absolute_path))
        )

    def extract(self, source: str) -> Mapping[str, object]:
        if not source.startswith("---\n"):
            return {}
        _, frontmatter, _ = source.split("---\n", 2)
        payload = ConfigurationSchemaMapping.model_validate(safe_load(frontmatter)).root
        return ConfigurationSchemaMapping.model_validate(payload.get("config", {})).root

    def supports(self, contract: DiagramConfigurationContract, upstream: MermaidDiagramConfig) -> bool:
        if contract.config_key != upstream.config_key or contract.schema_definition != upstream.schema_definition:
            return False
        document = ConfigurationSchemaDocument.model_validate(self.schema)
        expected = {"$ref": f"#/$defs/{upstream.schema_definition}"}
        property_schema = document.properties.get(upstream.config_key)
        return (
            property_schema is not None
            and property_schema.root == expected
            and upstream.schema_definition in document.definitions
        )

    def compare(
        self,
        config_key: str,
        local: Mapping[str, object],
        upstream: MermaidDiagramConfig,
    ) -> tuple[ConfigurationViolation, ...]:
        document = ConfigurationSchemaDocument.model_validate(self.schema)
        expected = self.properties(self.schema, upstream.schema)
        expected["wrap"] = document.properties["wrap"].root
        actual = self.properties(local, local)
        differences = self.compare_properties(config_key, "", local, actual, self.schema, expected)

        violations: list[ConfigurationViolation] = []
        for path, facets in differences.items():
            override = self.overrides.get(path)
            if override is None:
                violations.append(
                    ConfigurationViolation(path, f"configuration schema differs in facets: {', '.join(sorted(facets))}")
                )
            elif override.facets != facets:
                violations.append(
                    ConfigurationViolation(
                        path,
                        "override facets "
                        f"{', '.join(sorted(override.facets))} do not match observed facets "
                        f"{', '.join(sorted(facets))}",
                    )
                )
        for path in sorted(self.overrides):
            if path.startswith(f"{config_key}.") and path not in differences:
                violations.append(ConfigurationViolation(path, "configuration override is stale"))
        return tuple(violations)

    def compare_properties(
        self,
        config_key: str,
        parent: str,
        local_root: Mapping[str, object],
        local: Mapping[str, object],
        upstream_root: Mapping[str, object],
        upstream: Mapping[str, object],
    ) -> dict[str, frozenset[str]]:
        differences: dict[str, frozenset[str]] = {}
        for name in sorted(local.keys() | upstream.keys()):
            property_path = f"{parent}.{name}" if parent else name
            path = f"{config_key}.{property_path}"
            if name not in local:
                differences[path] = frozenset({"unsupported"})
                continue
            if name not in upstream:
                differences[path] = frozenset({"alias"})
                continue
            local_schema = self.resolve(local_root, ConfigurationSchemaMapping.model_validate(local[name]).root)
            upstream_schema = self.resolve(
                upstream_root,
                ConfigurationSchemaMapping.model_validate(upstream[name]).root,
            )
            local_container = ConfigurationSchemaContainer.model_validate(local_schema)
            upstream_container = ConfigurationSchemaContainer.model_validate(upstream_schema)
            facets = frozenset(
                facet
                for facet in self.facets
                if self.facet(local_root, local_schema, facet) != self.facet(upstream_root, upstream_schema, facet)
            )
            if facets:
                differences[path] = facets
            if local_container.allows_additional_properties != upstream_container.allows_additional_properties:
                differences[f"{path}.additionalProperties"] = frozenset({"policy"})
            local_children = local_container.children()
            upstream_children = upstream_container.children()
            if local_children or upstream_children:
                differences.update(
                    self.compare_properties(
                        config_key,
                        property_path,
                        local_root,
                        local_children,
                        upstream_root,
                        upstream_children,
                    )
                )
        return differences

    def properties(
        self,
        root: Mapping[str, object],
        value: Mapping[str, object],
    ) -> dict[str, object]:
        resolved = self.resolve(root, value)
        return ConfigurationSchemaContainer.model_validate(resolved).children()

    def resolve(
        self,
        root: Mapping[str, object],
        value: Mapping[str, object],
    ) -> dict[str, object]:
        resolved: dict[str, object] = {}
        reference = ConfigurationSchemaReference.model_validate(value.get("$ref")).root
        reference_value = ConfigurationSchemaReference(root=reference)
        if reference_value.internal:
            target = ConfigurationSchemaMapping(root=root)
            for segment in reference_value.segments:
                target = ConfigurationSchemaMapping.model_validate(target.root[segment])
            resolved.update(self.resolve(root, target.root))
        all_of = ConfigurationSchemaMappings.model_validate(value.get("allOf", ())).root
        for item in all_of:
            inherited = self.resolve(root, item.root)
            resolved.update({key: child for key, child in inherited.items() if key != "properties"})
            inherited_properties = ConfigurationSchemaProperties.model_validate(
                inherited.get("properties", {})
            ).root
            properties = ConfigurationSchemaProperties.model_validate(
                resolved.setdefault("properties", {})
            ).root
            resolved["properties"] = {
                **{name: child.root for name, child in properties.items()},
                **{name: child.root for name, child in inherited_properties.items()},
            }
        for key, item in value.items():
            if key not in {"$ref", "allOf", "properties"}:
                resolved[key] = item
        if "properties" in value:
            properties = ConfigurationSchemaProperties.model_validate(
                resolved.setdefault("properties", {})
            ).root
            local_properties = ConfigurationSchemaProperties.model_validate(value["properties"]).root
            resolved["properties"] = {
                **{name: child.root for name, child in properties.items()},
                **{name: child.root for name, child in local_properties.items()},
            }
        return resolved

    def facet(
        self,
        root: Mapping[str, object],
        value: Mapping[str, object],
        facet: str,
    ) -> ConfigurationSchemaFacet:
        resolved = self.resolve(root, value)
        alternatives = ConfigurationSchemaMappings.model_validate(
            resolved.get("anyOf", resolved.get("oneOf", ()))
        ).root
        if facet in {"type", "nullability"}:
            types = set(ConfigurationSchemaTypes.model_validate(resolved.get("type")).values)
            for alternative in alternatives:
                alternative_type = self.facet(root, alternative.root, "type")
                types.update(ConfigurationSchemaStrings.model_validate(alternative_type.value).root)
            if facet == "nullability":
                return ConfigurationSchemaFacet(True, "null" in types)
            return ConfigurationSchemaFacet(True, tuple(sorted(types - {"null"})))
        if facet == "enum":
            return ConfigurationSchemaFacet(
                "enum" in resolved,
                ConfigurationSchemaEnumeration.model_validate(resolved.get("enum")).values,
            )
        value = ConfigurationSchemaFacet(facet in resolved, resolved.get(facet))
        if facet not in {"minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum", "multipleOf"}:
            return value
        nested = tuple(
            ConfigurationSchemaAlternativeFacet(
                self.facet(root, alternative.root, "type"),
                candidate,
            )
            for alternative in alternatives
            if (candidate := self.facet(root, alternative.root, facet)).present
        )
        return ConfigurationSchemaFacet(value.present, value.value, nested)

    def partial_schema(self) -> dict[str, object]:
        return ConfigurationSchemaMapping.model_validate(
            ConfigurationSchemaNode.model_validate(dict(self.schema)).without_required()
        ).root
