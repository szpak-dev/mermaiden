import argparse
import ast
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

REQUIRED_APPLICATION_OPERATIONS = {
    "apply_batch",
    "available_diagrams",
    "close",
    "command_payload",
    "create",
    "create_diagram",
    "diagram_description",
    "diagram_info",
    "execute",
    "mermaid_cli_version",
    "mermaid_version",
    "render",
    "restore",
    "snapshot",
    "snapshot_contract_identity",
    "validate_render",
    "write_preview",
}

FORBIDDEN_TEST_IMPORTS = {"ast", "inspect", "subprocess", "unittest.mock", "wireup"}


class Authority(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    record_id: str
    record_content_revision: str
    resource_path: str
    resource_revision: str


class ApplicationTestFreeze(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    authorities: tuple[Authority, ...] = Field(min_length=2, max_length=2)
    files: dict[str, str] = Field(min_length=1)


@dataclass(frozen=True, order=True)
class Violation:
    path: str
    line: int
    detail: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.detail}"


class ApplicationTestCheck:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.violations: list[Violation] = []

    def run(self, arguments: tuple[str, ...]) -> int:
        parser = argparse.ArgumentParser()
        parser.add_argument("--print-freeze", action="store_true")
        parser.add_argument("--write-freeze", action="store_true")
        parser.add_argument("--check-freeze", action="store_true")
        options = parser.parse_args(arguments)
        self.check_policy()
        if options.check_freeze:
            self.check_freeze()
        if self.violations:
            for violation in sorted(self.violations):
                print(violation.render(), file=sys.stderr)
            print(f"Application test policy: {len(self.violations)} violation(s).", file=sys.stderr)
            return 1
        if options.print_freeze:
            print(json.dumps(self.current_freeze().model_dump(mode="json"), indent=2) + "\n", end="")
            return 0
        if options.write_freeze:
            path = self.root / "tests" / "application-suite.freeze.json"
            payload = json.dumps(self.current_freeze().model_dump(mode="json"), indent=2) + "\n"
            path.write_text(payload, encoding="utf-8")
            print(f"Application test freeze written: {path.relative_to(self.root)}")
            return 0
        print("Application test policy: no violations.")
        return 0

    def check_policy(self) -> None:
        operation_evidence = dict.fromkeys(REQUIRED_APPLICATION_OPERATIONS, 0)
        for path in sorted((self.root / "tests").rglob("*.py")):
            relative = str(path.relative_to(self.root))
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
            application_imports = 0
            is_test_module = path.name.startswith("test_")
            for node in ast.walk(tree):
                if type(node) is ast.ImportFrom:
                    if node.module == "mermaiden":
                        names = tuple(alias.name for alias in node.names)
                        if names == ("Application",):
                            application_imports += 1
                        else:
                            self.add(relative, node.lineno, "product imports must contain only mermaiden.Application")
                    elif node.module is not None and node.module.startswith("mermaiden."):
                        self.add(relative, node.lineno, "tests must not import Mermaiden implementation modules")
                    elif node.module in FORBIDDEN_TEST_IMPORTS:
                        self.add(relative, node.lineno, f"tests must not inspect or drive {node.module}")
                elif type(node) is ast.Import:
                    for alias in node.names:
                        if alias.name == "mermaiden" or alias.name.startswith("mermaiden."):
                            self.add(relative, node.lineno, "tests must import only mermaiden.Application")
                        if alias.name in FORBIDDEN_TEST_IMPORTS:
                            self.add(relative, node.lineno, f"tests must not inspect or drive {alias.name}")
                elif type(node) is ast.FunctionDef and node.name.startswith("test_") and is_test_module:
                    names = {item.id for item in ast.walk(node) if type(item) is ast.Name}
                    if "Application" not in names and "application" not in names:
                        self.add(relative, node.lineno, "test does not exercise the public Application boundary")
                elif type(node) is ast.Dict and is_test_module:
                    identifier_keys = {
                        "after_id",
                        "before_id",
                        "box_id",
                        "child_id",
                        "class_id",
                        "component_id",
                        "element_id",
                        "entity_id",
                        "group_id",
                        "id",
                        "lane_id",
                        "owner_id",
                        "parent_id",
                        "participant_id",
                        "period_id",
                        "section_id",
                        "set_id",
                        "source_id",
                        "target_id",
                        "task_id",
                    }
                    for key, value in zip(node.keys, node.values, strict=True):
                        if type(key) is not ast.Constant or key.value not in identifier_keys:
                            continue
                        if type(value) is not ast.Constant or type(value.value) is not str:
                            continue
                        identifier = value.value
                        if (
                            identifier
                            and identifier != "$root"
                            and not identifier.startswith("example")
                            and not identifier.endswith("example")
                        ):
                            self.add(
                                relative,
                                value.lineno,
                                f"invented identifier {identifier!r} is not neutral example data",
                            )
                elif type(node) is ast.Name and node.id in {
                    "MagicMock",
                    "Mock",
                    "MermaidenCli",
                    "monkeypatch",
                    "patch",
                }:
                    self.add(relative, node.lineno, f"forbidden test seam {node.id!r}")
                elif type(node) is ast.Attribute:
                    if node.attr in operation_evidence:
                        operation_evidence[node.attr] += 1
                    if node.attr in {
                        "find_annotations",
                        "find_element",
                        "find_relations",
                        "report",
                        "root_elements",
                        "walk_elements",
                    }:
                        self.add(relative, node.lineno, f"private implementation observation {node.attr!r}")
            if is_test_module and application_imports != 1:
                self.add(relative, 1, "every product test module must import mermaiden.Application exactly once")
            elif not is_test_module and application_imports > 1:
                self.add(relative, 1, "test support modules may import mermaiden.Application at most once")
        for operation, count in operation_evidence.items():
            if count == 0:
                self.add("tests", 1, f"public Application operation {operation!r} has no test evidence")

    def check_freeze(self) -> None:
        path = self.root / "tests" / "application-suite.freeze.json"
        expected = ApplicationTestFreeze.model_validate_json(path.read_text(encoding="utf-8"))
        observed = self.current_freeze()
        if observed != expected:
            self.add(str(path.relative_to(self.root)), 1, "frozen test inputs changed")

    def current_freeze(self) -> ApplicationTestFreeze:
        paths = (*sorted((self.root / "tests").rglob("*.py")), self.root / "pyproject.toml")
        return ApplicationTestFreeze(
            schema_version=1,
            authorities=(
                Authority(
                    record_id="AxTPtEU9S9mt54z6yjEAi2",
                    record_content_revision="803dd2a7d5d548f9e6598f1891fc789192dc6e08bff9995259b916571e5686ec",
                    resource_path="guidance/fortress-siege-and-meticulous-auntie.md",
                    resource_revision="8d65c45e8221949198c4c9fc8deba90ca9005f1ba5e0859541e628bc9a8a5502",
                ),
                Authority(
                    record_id="tzMYbAN4rHxGYTEji6yRqF",
                    record_content_revision="90b049bedefae526587e17f351f0bff202f590e36c36df9a629f898f8bda6ed9",
                    resource_path="guidance/behavioral-verification.md",
                    resource_revision="cbf935ca4d74325d8f9d5fd15474178fcda83d48035a5b4c5d20d8b697acd3b8",
                ),
            ),
            files={str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        )

    def add(self, path: str, line: int, detail: str) -> None:
        self.violations.append(Violation(path, line, detail))


if __name__ == "__main__":
    raise SystemExit(ApplicationTestCheck(Path(__file__).resolve().parents[1]).run(tuple(sys.argv[1:])))
