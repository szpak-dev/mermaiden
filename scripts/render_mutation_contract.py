from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "docs" / "contracts" / "diagram-mutations"
CONTRACT_PATH = CONTRACT_ROOT / "contract.json"
DIAGRAMS_PATH = CONTRACT_ROOT / "diagrams"
DOCUMENT_PATH = CONTRACT_ROOT / "README.md"

JsonObject = dict[str, Any]


def load_contract(path: Path = CONTRACT_PATH) -> JsonObject:
    contract = _read_object(path)
    diagrams: JsonObject = {}
    for diagram_path in sorted(DIAGRAMS_PATH.glob("*.json")):
        diagram = _read_object(diagram_path)
        diagram_id = diagram.pop("diagram_id", None)
        if diagram_id != diagram_path.stem:
            raise ValueError(f"Diagram ID {diagram_id!r} must match filename '{diagram_path.name}'.")
        diagrams[diagram_path.stem] = diagram
    if not diagrams:
        raise ValueError(f"No diagram contracts found under '{DIAGRAMS_PATH}'.")
    contract["diagrams"] = diagrams
    return contract


def render_documents(contract: Mapping[str, Any]) -> dict[Path, str]:
    classifications = _object(contract["classifications"], "classifications")
    diagrams = _object(contract["diagrams"], "diagrams")
    documents = {DOCUMENT_PATH: render_overview(contract)}
    for diagram_id, value in diagrams.items():
        diagram = _object(value, f"diagrams.{diagram_id}")
        documents[DIAGRAMS_PATH / f"{diagram_id}.md"] = render_diagram(diagram_id, diagram, classifications)
    return documents


def render_overview(contract: Mapping[str, Any]) -> str:
    lines = [
        "# Diagram mutation contract",
        "",
        "This documentation is generated from `contract.json` and `diagrams/*.json`.",
        "Run `make mutation-contract` after changing the machine-readable sources.",
        "",
        f"Contract version: `{contract['contract_version']}`.",
        "",
        "## Classifications",
        "",
        "| Classification | Meaning |",
        "| --- | --- |",
    ]
    for name, description in _object(contract["classifications"], "classifications").items():
        lines.append(f"| `{name}` | {_escape(str(description))} |")
    lines.extend(("", "## Semantics", ""))
    for item in _list(contract["semantics"], "semantics"):
        semantic = _object(item, "semantics[]")
        lines.append(f"- **{semantic['name']}.** {semantic['rule']}")
    lines.extend(
        (
            "",
            "## Commands",
            "",
            "| Operation | Applies to | Required payload | Strictness |",
            "| --- | --- | --- | --- |",
        )
    )
    for operation, item in _object(contract["commands"], "commands").items():
        command = _object(item, f"commands.{operation}")
        payload = _object(command["payload_schema"], f"commands.{operation}.payload_schema")
        required = ", ".join(f"`{name}`" for name in _strings(payload["required"], "required"))
        strictness = "unknown fields rejected" if payload.get("additionalProperties") is False else "open"
        lines.append(f"| `{operation}` | {command['applies_to']} | {required} | {strictness} |")
    lines.extend(("", "Dynamic schema sources:", ""))
    sources = _object(contract["payload_schema_sources"], "payload_schema_sources")
    for source, description in sources.items():
        lines.append(f"- `{source}`: {description}")
    lines.extend(
        (
            "",
            "## Applicability matrix",
            "",
            "| Diagram | Elements | Relations | Annotations |",
            "| --- | ---: | ---: | ---: |",
        )
    )
    for diagram_id, value in _object(contract["diagrams"], "diagrams").items():
        diagram = _object(value, f"diagrams.{diagram_id}")
        lines.append(
            f"| [`{diagram_id}`](diagrams/{diagram_id}.md)"
            f" | {len(_object(diagram['elements'], 'elements'))}"
            f" | {len(_object(diagram['relations'], 'relations'))}"
            f" | {len(_object(diagram['annotations'], 'annotations'))} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def render_diagram(
    diagram_id: str,
    diagram: Mapping[str, Any],
    classifications: Mapping[str, Any],
) -> str:
    root = _object(diagram["root_collection"], f"diagrams.{diagram_id}.root_collection")
    lines = [
        f"# `{diagram_id}` mutation matrix",
        "",
        f"Generated from [`{diagram_id}.json`]({diagram_id}.json). Do not edit directly.",
        "",
        f"Root ordering: `{root['reorder_command']}` over the exact direct-member permutation.",
        "",
    ]
    for category, title in (
        ("elements", "Elements"),
        ("relations", "Relations"),
        ("annotations", "Annotations"),
    ):
        objects = _object(diagram[category], f"diagrams.{diagram_id}.{category}")
        lines.extend((f"## {title}", ""))
        if not objects:
            lines.extend(("None.", ""))
            continue
        lines.extend(
            (
                "| Kind | Update command | Placement or retargeting | Fields |",
                "| --- | --- | --- | --- |",
            )
        )
        for kind, object_value in objects.items():
            item = _object(object_value, f"diagrams.{diagram_id}.{category}.{kind}")
            context = _context(category, item)
            fields = _field_policy(
                _object(item["fields"], f"{diagram_id}.{category}.{kind}.fields"),
                classifications,
            )
            lines.append(f"| `{kind}` | `{item['update_command']}` | {_escape(context)} | {_escape(fields)} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _context(category: str, item: Mapping[str, Any]) -> str:
    if category == "elements":
        placement = _object(item["placement"], "placement")
        parents = ", ".join(f"`{name}`" for name in _strings(placement["allowed_parents"], "allowed_parents"))
        child_order = "; direct children use `reorder_elements`" if "child_collection" in item else ""
        return f"parents: {parents}; move: `{placement['move_command']}`{child_order}"
    retargeting = _object(item["retargeting"], "retargeting")
    return f"`{retargeting['field']}` via `{item['update_command']}`; ordered: `{str(retargeting['ordered']).lower()}`"


def _field_policy(fields: Mapping[str, Any], classifications: Mapping[str, Any]) -> str:
    groups: dict[str, list[str]] = {name: [] for name in classifications}
    for field_name, classification_value in fields.items():
        classification = str(classification_value)
        if classification not in groups:
            raise ValueError(f"Unknown classification {classification!r} for field {field_name!r}.")
        groups[classification].append(f"`{field_name}`")
    return "; ".join(f"{classification}: {', '.join(names)}" for classification, names in groups.items() if names)


def _escape(value: str) -> str:
    return value.replace("|", "\\|")


def _read_object(path: Path) -> JsonObject:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Mutation contract at '{path}' must be a JSON object.")
    return cast(JsonObject, value)


def _object(value: object, path: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ValueError(f"'{path}' must be an object.")
    return cast(JsonObject, value)


def _list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"'{path}' must be an array.")
    return cast(list[object], value)


def _strings(value: object, path: str) -> tuple[str, ...]:
    items = _list(value, path)
    result: list[str] = []
    for item in items:
        if not isinstance(item, str):
            raise ValueError(f"'{path}' must contain only strings.")
        result.append(item)
    return tuple(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the public diagram mutation contract.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="replace generated Markdown")
    mode.add_argument("--check", action="store_true", help="fail when generated Markdown has drifted")
    arguments = parser.parse_args()
    documents = render_documents(load_contract())
    if arguments.write:
        for path, rendered in documents.items():
            path.write_text(rendered, encoding="utf-8")
        expected = set(documents)
        for path in DIAGRAMS_PATH.glob("*.md"):
            if path not in expected:
                path.unlink()
        return
    if arguments.check:
        drifted = [
            path
            for path, rendered in documents.items()
            if not path.exists() or path.read_text(encoding="utf-8") != rendered
        ]
        expected = set(documents)
        drifted.extend(path for path in DIAGRAMS_PATH.glob("*.md") if path not in expected)
        if drifted:
            names = ", ".join(str(path.relative_to(ROOT)) for path in sorted(drifted))
            raise SystemExit(f"Generated mutation contract is stale ({names}); run `make mutation-contract`.")
        return
    print(documents[DOCUMENT_PATH], end="")


if __name__ == "__main__":
    main()
