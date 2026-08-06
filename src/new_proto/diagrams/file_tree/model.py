from new_proto.core import Container, Diagram, Element, Entity


class Entry(Entity):
    def __init__(self, entry_id: str, name: str) -> None:
        Element.__init__(self)
        self._id = entry_id
        self.name = name

    @property
    def id(self) -> str:
        return self._id

    def rename(self, name: str) -> None:
        self.name = name

    def behaviours(self):
        from .behaviours import RenameEntry

        return (*super().behaviours(), RenameEntry(self))


class File(Entry):
    @property
    def kind(self) -> str:
        return "file"


class Directory(Entry, Container):
    def __init__(self, directory_id: str, name: str) -> None:
        Entry.__init__(self, directory_id, name)
        self._init_container()

    @property
    def kind(self) -> str:
        return "directory"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, Entry)

    def add_file(self, name: str, *, file_id: str | None = None, after_id: str | None = None) -> File:
        file = File(file_id or self.new_id("file"), name)
        self.add(file, after_id=after_id)
        return file

    def add_directory(self, name: str, *, directory_id: str | None = None, after_id: str | None = None) -> Directory:
        directory = Directory(directory_id or self.new_id("directory"), name)
        self.add(directory, after_id=after_id)
        return directory

    def behaviours(self):
        from .behaviours import AddDirectory, AddFile

        return (*super().behaviours(), AddFile(self), AddDirectory(self))


class FileTree(Diagram):
    @property
    def diagram_type(self) -> str:
        return "file-tree"

    def accepts(self, child: Element) -> bool:
        return isinstance(child, Entry)

    def add_file(self, name: str, *, file_id: str | None = None, after_id: str | None = None) -> File:
        file = File(file_id or self.new_id("file"), name)
        self.add(file, after_id=after_id)
        return file

    def add_directory(self, name: str, *, directory_id: str | None = None, after_id: str | None = None) -> Directory:
        directory = Directory(directory_id or self.new_id("directory"), name)
        self.add(directory, after_id=after_id)
        return directory

    def move_entry(self, entry_id: str, *, destination_id: str | None = None, after_id: str | None = None) -> None:
        entry = self.find(entry_id)
        if not isinstance(entry, Entry) or entry.parent is None:
            raise KeyError(f"No movable file-tree entry {entry_id!r}")
        destination: Container = self if destination_id is None else self.find(destination_id)
        if not isinstance(destination, FileTree | Directory):
            raise TypeError("File-tree entries can only be moved to a directory or the root")
        entry.parent.remove(entry_id)
        destination.add(entry, after_id=after_id)

    def behaviours(self):
        from .behaviours import AddDirectory, AddFile, MoveEntry

        return (*super().behaviours(), AddFile(self), AddDirectory(self), MoveEntry(self))
