from enum import StrEnum

from ...core.domain import Entity


class TreeItemType(StrEnum):
    ITEM = "item"
    DIRECTORY = "directory"
    FILE = "file"


class TreeItem(Entity):
    item_type: TreeItemType = TreeItemType.ITEM

    @property
    def rendered_label(self) -> str:
        return f"{self.label}/" if self.item_type is TreeItemType.DIRECTORY else self.label
