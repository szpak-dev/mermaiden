import re

from pydantic import BaseModel, ConfigDict


class ValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    def __init__(self, *arguments: object, **values: object) -> None:
        names = tuple(type(self).model_fields)
        if len(arguments) > len(names):
            raise TypeError(f"{type(self).__name__} accepts at most {len(names)} positional arguments.")
        positional = dict(zip(names, arguments))
        duplicates = positional.keys() & values.keys()
        if duplicates:
            raise TypeError(f"{type(self).__name__} received duplicate fields: {', '.join(sorted(duplicates))}.")
        super().__init__(**positional, **values)


class ClassifiedValueModel(ValueModel):
    @property
    def kind(self) -> str:
        return type(self).kind_for()

    @classmethod
    def kind_for(cls) -> str:
        boundary = re.sub("([A-Z]+)([A-Z][a-z])", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", boundary).lower()
