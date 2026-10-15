# The Mermaid boundary

Generating Mermaid text and proving that Mermaid can lay it out are related but distinct operations.

`Application.render()` stays inside the Python process. It checks the diagram, selects the registered Jinja template,
and formats deterministic source. This path is suitable for ordinary application requests and needs no browser or
Mermaid executable.

`Application.validate_render()` crosses an external-process boundary. It runs the compatible `mmdc` executable, which in
turn needs a browser, and returns SVG plus structured diagnostics. That proof catches failures that source inspection
cannot: parser differences, layout failures, missing browser support, and CLI compatibility problems.

Mermaiden pins the upstream Mermaid version and configuration schema in the package. Configuration models are compared
with that checked content, while reviewed differences remain explicit. The `compat` CLI checks this contract without
performing a full SVG rendering pass.

Keeping the paths separate matters in production. A service that only needs Mermaid source should not pay browser
startup cost or inherit browser deployment risk. A release or integration environment can run the complete validation
tier where the stronger evidence is worth that cost.
