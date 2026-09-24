from collections.abc import Mapping, Sequence
from functools import singledispatchmethod
from typing import cast

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema
from pydantic_core import CoreSchema, SchemaSerializer, SchemaValidator, core_schema

from ..domain import CommandArguments, CommandPayload


class PydanticCommandPayload(CommandPayload):
    def __init__(self, schema: CoreSchema, invocation_defaults: Sequence[str], description: str = "") -> None:
        definitions: dict[str, CoreSchema] = {}
        normalized = cast(CoreSchema, self._collect_definitions(schema, definitions))
        self._schema = core_schema.definitions_schema(normalized, list(definitions.values()))
        self._invocation_defaults = frozenset(invocation_defaults)
        self._description = description
        self._validator = SchemaValidator(self._schema)
        self._serializer = SchemaSerializer(self._schema)

    @singledispatchmethod
    def _collect_definitions(self, value: object, definitions: dict[str, CoreSchema]) -> object:
        return value

    @_collect_definitions.register(dict)
    def _(self, value: dict[str, object], definitions: dict[str, CoreSchema]) -> object:
        if value.get("type") != "definitions":
            return {key: self._collect_definitions(item, definitions) for key, item in value.items()}
        for definition in cast(list[dict[str, object]], value["definitions"]):
            reference = cast(str, definition["ref"])
            if reference not in definitions:
                definitions[reference] = cast(CoreSchema, self._collect_definitions(definition, definitions))
        return self._collect_definitions(value["schema"], definitions)

    @_collect_definitions.register(list)
    def _(self, value: list[object], definitions: dict[str, CoreSchema]) -> object:
        return [self._collect_definitions(item, definitions) for item in value]

    def validate(self, arguments: Mapping[str, object]) -> CommandArguments:
        validated = self._validator.validate_python(arguments)
        python_values = cast(dict[str, object], self._serializer.to_python(validated))
        json_values = cast(dict[str, object], self._serializer.to_python(validated, mode="json", by_alias=True))
        invocation_fields = frozenset(arguments).union(self._invocation_defaults)
        invocation = {name: python_values[name] for name in invocation_fields}
        return CommandArguments(json_values, invocation)

    def schema(self) -> Mapping[str, object]:
        schema = GenerateJsonSchema().generate(self._schema)
        if self._description:
            schema["description"] = self._description
        return schema


class PydanticModelCommandPayload(CommandPayload):
    def __init__(self, model: type[BaseModel], argument_name: str) -> None:
        self._model = model
        self._argument_name = argument_name

    def validate(self, arguments: Mapping[str, object]) -> CommandArguments:
        validated = self._model.model_validate(arguments)
        values = cast(dict[str, object], validated.model_dump(mode="json", by_alias=True))
        return CommandArguments(values, {self._argument_name: validated})

    def schema(self) -> Mapping[str, object]:
        return self._model.model_json_schema()
