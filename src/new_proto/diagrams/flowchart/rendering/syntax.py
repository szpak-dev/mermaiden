import base64
import json
import re

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_-]+$")


def mermaid_identifier(value: object, namespace: str) -> str:
    text = str(value)
    if _SAFE_IDENTIFIER.fullmatch(text):
        token = f"v_{text}"
    else:
        encoded = base64.b32encode(text.encode()).decode().rstrip("=").lower()
        token = f"b_{encoded}"
    return f"{namespace}_{token}"


def mermaid_quote(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


__all__ = ["mermaid_identifier", "mermaid_quote"]
