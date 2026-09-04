import re
from typing import Annotated

from pydantic import Field

from ...core import domain

_ENTITY_ATTRIBUTE_DATA_TYPE_PATTERN = re.compile(
    r"^(?![\s\S]*[\r\n])(?!(?:[Pp][Kk]|[Ff][Kk]|[Uu][Kk])(?:$|[^A-Za-z0-9_]))"
    r"(?:[\*A-Za-z_\u00C0-\uFFFF][A-Za-z0-9\-\_\[\]\(\)\.,\u00C0-\uFFFF\*]*\??"
    r"|[^\s]*~[^\r\n]*~[^\s]*|`[^`]+`\??)$"
)
EntityAttributeDataType = Annotated[str, Field(pattern=_ENTITY_ATTRIBUTE_DATA_TYPE_PATTERN)]


class EntityAttribute(domain.Entity):
    data_type: EntityAttributeDataType = "string"
    keys: tuple[str, ...] = ()
    comment: str = ""


class Entity(domain.Container):
    pass
