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

`validate_render()` invokes `mmdc` from `PATH`. Read `application.mermaid_version`, then install that exact CLI version:

```sh
MMD_VERSION="$(python -c 'from mermaiden import Application as A; print(A.create().mermaid_version)')"
npm install --global "@mermaid-js/mermaid-cli@${MMD_VERSION}"
mmdc --version
```

The final command must print the same version. Mermaid CLI installs its Puppeteer browser by default. If that download
was disabled or the environment supplies its own compatible Chrome or Chromium executable, set
`PUPPETEER_EXECUTABLE_PATH` before calling `validate_render()`.

The report keeps SVG output, the expected Mermaid version, and structured diagnostics together. Missing executables,
version mismatches, timeouts, Mermaid failures, and invalid SVG output each produce a distinct diagnostic.

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
