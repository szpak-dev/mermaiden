from new_proto.core import Behaviour

from .model import Directory, Entry, FileTree


class RenameEntry(Behaviour):
    @property
    def name(self) -> str:
        return "rename_entry"

    def execute(self, *, name: str) -> Entry:
        owner = self.owner
        assert isinstance(owner, Entry)
        owner.rename(name)
        return owner


class AddFile(Behaviour):
    @property
    def name(self) -> str:
        return "add_file"

    def execute(self, *, name: str, file_id: str | None = None, after_id: str | None = None):
        owner = self.owner
        assert isinstance(owner, Directory | FileTree)
        return owner.add_file(name, file_id=file_id, after_id=after_id)


class AddDirectory(Behaviour):
    @property
    def name(self) -> str:
        return "add_directory"

    def execute(self, *, name: str, directory_id: str | None = None, after_id: str | None = None):
        owner = self.owner
        assert isinstance(owner, Directory | FileTree)
        return owner.add_directory(name, directory_id=directory_id, after_id=after_id)


class MoveEntry(Behaviour):
    @property
    def name(self) -> str:
        return "move_entry"

    def execute(self, *, entry_id: str, destination_id: str | None = None, after_id: str | None = None) -> None:
        owner = self.owner
        assert isinstance(owner, FileTree)
        owner.move_entry(entry_id, destination_id=destination_id, after_id=after_id)
