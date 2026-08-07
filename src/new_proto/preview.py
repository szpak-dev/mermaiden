import argparse
from html import escape
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", type=Path, nargs="+")
    parser.add_argument("--output", "-o", type=Path, default=Path(".preview/index.html"))
    arguments = parser.parse_args()
    sections = "\n".join(
        "<section>"
        f"<h2>{escape(source.stem)}</h2>"
        f"<pre class=\"mermaid\">{escape(source.read_text(encoding='utf-8'))}</pre>"
        "</section>"
        for source in arguments.sources
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Mermaid previews</title>
<style>body {{ font-family: sans-serif; margin: 2rem; }} section {{ margin-block: 3rem; }}</style>
<body>
{sections}
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({{ startOnLoad: true }});
</script>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(arguments.output)


if __name__ == "__main__":
    main()
