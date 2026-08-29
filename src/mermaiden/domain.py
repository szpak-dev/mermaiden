from typing import Protocol


class ValidatedCommandPayload(Protocol):
    def model_dump(self, *, exclude_unset: bool = False) -> dict[str, object]: ...


class CommandPayloadType(Protocol):
    def model_validate(self, value: object) -> ValidatedCommandPayload: ...

    def model_json_schema(self) -> dict[str, object]: ...
