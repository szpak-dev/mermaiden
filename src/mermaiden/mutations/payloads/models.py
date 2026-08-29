from typing import Self

from pydantic import ConfigDict, model_validator

from ...core.model import ValueModel


class MutationChanges(ValueModel):
    model_config = ConfigDict(json_schema_extra={"minProperties": 1})

    @model_validator(mode="after")
    def require_change(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Changes must contain at least one field.")
        return self
