import json


def tree_label(value: object) -> str:
    text = str(value)
    if not text or text != text.strip() or "  " in text or any(token in text for token in ('"', ":::", "##")):
        return json.dumps(text, ensure_ascii=False)
    return text


__all__ = ["tree_label"]
