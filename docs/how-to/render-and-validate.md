# Render and validate Mermaid

Choose the lightest operation that proves what you need. Deterministic source generation and full Mermaid rendering have
different dependencies and failure modes.

## Generate Mermaid source

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("pie")
    application.execute(diagram, "add_slice", {"id": "typed", "label": "Typed", "value": 70})
    application.execute(diagram, "add_slice", {"id": "other", "label": "Other", "value": 30})
    source = application.render(diagram)

    assert "\npie\n" in source
```

`render()` validates the complete diagram and returns Mermaid text. It does not start Node.js, a browser, or `mmdc`.
Invalid drafts are rejected with their blocking diagnostics.

Journey and Timeline serialize titles, labels, and actor names as text. Punctuation and words such as `title` or
`section` remain literal values; they cannot introduce Mermaid delimiters or statements.

Class diagrams use native SVG text for labels and default to ELK layout. Generated source sets root-level
`config.htmlLabels: false`; the class-diagram `configure` command does not expose `htmlLabels`.

## Run full SVG validation

```python
from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("pie")
    application.execute(diagram, "add_slice", {"id": "typed", "label": "Typed", "value": 70})
    application.execute(diagram, "add_slice", {"id": "other", "label": "Other", "value": 30})
    report = application.validate_render(diagram)
    if not report.success:
        raise RuntimeError(report.diagnostics)
    svg = report.svg
```

`validate_render()` invokes `mmdc` from `PATH`. Mermaiden does not package Node.js, Mermaid, Mermaid CLI, Puppeteer, or a
browser. The calling environment owns that runtime and must install the exact Mermaid engine and CLI versions exposed by
the installed Mermaiden release:

```sh
MERMAID_VERSION="$(python -c 'from mermaiden import Application as A; print(A.create().mermaid_version)')"
MMD_CLI_VERSION="$(python -c 'from mermaiden import Application as A; print(A.create().mermaid_cli_version)')"
npm install --save-exact "mermaid@${MERMAID_VERSION}" "@mermaid-js/mermaid-cli@${MMD_CLI_VERSION}"
python -m mermaiden.cli renderer-setup
npx puppeteer browsers install
export PATH="$PWD/node_modules/.bin:$PATH"
mmdc --version
```

The final command must print `MMD_CLI_VERSION`. `npx puppeteer browsers install` provisions the browser selected by the
Puppeteer version installed with Mermaid CLI. A deployment image should run these installation commands while building
the image; application startup should not download runtime dependencies. If the environment intentionally supplies a
compatible Chrome or Chromium executable instead, it may configure Puppeteer through `PUPPETEER_EXECUTABLE_PATH`.

`renderer-setup` applies Mermaiden's pinned native SVG text correction to the installed Mermaid package. It checks the
original and corrected file hashes, preserves already-correct installations, and rejects unexpected package contents.
Run it after installing or reinstalling npm dependencies. For a separate npm installation directory, use
`python -m mermaiden.cli renderer-setup --prefix /path/to/renderer`. In this repository, `npm install` and `npm ci`
apply the correction automatically through the package's installation script.

The correction decodes text once before measuring and wrapping SVG labels. Punctuation, Unicode, and literal
entity-looking input remain user text. Models and snapshots retain the original characters.

Before rendering, Mermaiden resolves `mmdc` through `PATH` and reads the installed CLI and engine package metadata. A
missing executable or package produces `renderer_unavailable`; either semver differing from the two public properties
produces `version_mismatch`. Missing or changed renderer patch files also produce `renderer_unavailable` before Mermaid
runs. Rendering never installs or modifies dependencies. The caller never supplies package paths or browser paths to
the rendering API.

The report keeps SVG output, the expected Mermaid engine and CLI versions, and structured diagnostics together. Missing
executables, CLI version mismatches, timeouts, Mermaid failures, and invalid SVG output each produce a distinct
diagnostic.

`Application.validate_sources(sources)` validates a mapping of names to Mermaid sources and returns reports in the
same order. It uses the same runtime checks and SVG validation as `validate_render()` and preview generation.
Configuration proof generation uses this operation as well. Empty input returns no reports; error placeholders and
non-finite SVG geometry are rejected.

## Supported Mermaid 12 line

| Authority | Supported version |
| --- | --- |
| Mermaid engine and configuration schema | `12.2.0` |
| `@mermaid-js/mermaid-cli` / `mmdc` | `12.0.0` |
| Required renderer correction | `native-svg-text-v2` |
| Node.js | `>=22.13.0`; this checkout pins `24.17.0` |
| Mermaiden snapshot contract | `v11` |

Run `make mermaid-freshness` to compare both configured authorities with the newest stable releases in the Mermaid
`12.x` line. Prereleases and versions from other major lines are intentionally ignored.

In a development checkout, install the Node lock and run the complete integration tier:

```sh
make integration
```

Repository contributors should use the lock rather than a global installation; it pins the same CLI version used in CI.

## Write a preview

To inspect several rendered sources in one browser page:

```python
from pathlib import Path

from mermaiden import Application

with Application.create() as application:
    diagram = application.create_diagram("pie")
    application.execute(diagram, "add_slice", {"id": "typed", "label": "Typed", "value": 70})
    application.execute(diagram, "add_slice", {"id": "other", "label": "Other", "value": 30})
    source = application.render(diagram)

    output = application.write_preview({"pie": source}, Path("diagram-preview.html"))
    assert output.exists()
```

Open `diagram-preview.html` in a browser. Choose any destination path owned by your application; Mermaiden does not open
the page or remove it after writing.

Preview creation requires the same installed renderer as `validate_render()`. Each diagram is rendered and checked
before the page is written. The page embeds the resulting SVGs and their fonts, with expandable source text, and needs
no CDN connection. A rendering failure leaves an existing destination file untouched.

Repository contributors can generate the complete fixture preview with `make diagrams-preview`. The local-only
`make diagrams-test` target generates it and opens the result with the platform `open` command.
