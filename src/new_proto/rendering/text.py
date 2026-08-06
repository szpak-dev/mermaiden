def canonical_text(value: str) -> str:
    """Return deterministic LF-only text with one trailing newline.

    Template indentation is preserved while trailing whitespace and surplus
    trailing lines are removed.
    """

    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = (line.rstrip() for line in normalized.rstrip("\n").split("\n"))
    return "\n".join(lines).rstrip("\n") + "\n"


__all__ = ["canonical_text"]
