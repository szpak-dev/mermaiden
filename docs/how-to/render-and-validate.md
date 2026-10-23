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
npx puppeteer browsers install
export PATH="$PWD/node_modules/.bin:$PATH"
mmdc --version
```

The final command must print `MMD_CLI_VERSION`. `npx puppeteer browsers install` provisions the browser selected by the
Puppeteer version installed with Mermaid CLI. A deployment image should run these installation commands while building
the image; application startup should not download runtime dependencies. If the environment intentionally supplies a
compatible Chrome or Chromium executable instead, it may configure Puppeteer through `PUPPETEER_EXECUTABLE_PATH`.

Before rendering, Mermaiden resolves `mmdc` through `PATH` and reads the installed CLI and engine package metadata. A
missing executable or package produces `renderer_unavailable`; either semver differing from the two public properties
produces `version_mismatch`. The caller never supplies package paths or browser paths to Mermaiden.

The report keeps SVG output, the expected Mermaid engine and CLI versions, and structured diagnostics together. Missing
executables, CLI version mismatches, timeouts, Mermaid failures, and invalid SVG output each produce a distinct
diagnostic.

## Supported Mermaid 12 line

| Authority | Supported version |
| --- | --- |
| Mermaid engine and configuration schema | `12.2.0` |
| `@mermaid-js/mermaid-cli` / `mmdc` | `12.0.0` |
| Node.js | `>=22.13.0`; this checkout pins `24.17.0` |
| Mermaiden snapshot contract | `v9`; earlier snapshots are rejected without migration |

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

Repository contributors can generate the complete fixture preview with `make diagrams-preview`. The local-only
`make diagrams-test` target generates it and opens the result with the platform `open` command.
