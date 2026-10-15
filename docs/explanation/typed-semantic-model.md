# The typed semantic model

Mermaid is a useful rendering language, but it is a poor place to hide application state. A raw source string cannot
tell an adapter which commands are legal, whether an identifier is stable, or which references would break after a
removal.

Mermaiden keeps that knowledge in typed diagram models. Each concrete diagram feature registers its elements, relations,
annotations, configuration, constraints, commands, snapshot identities, and Mermaid templates. The public `Application`
discovers and operates on that registry; callers do not import concrete feature classes.

This split produces three practical properties.

First, command payloads are strict JSON-shaped contracts. External values are validated and converted before domain code
uses them. Unknown fields and incompatible values do not drift into the diagram.

Second, the same semantic state drives discovery, mutation, persistence, and rendering. There is no handwritten REST
manifest beside a separate renderer inventory. When a feature changes, its registered definition remains the common
authority.

Third, Mermaid source becomes deterministic output. Templates format accepted typed state; they do not recover meaning
by parsing previously rendered text. A caller can store the snapshot, reproduce the source, and choose its own Markdown,
browser, or CLI rendering workflow.

The trade-off is deliberate strictness. Supporting a Mermaid syntax means modeling its useful concepts and constraints,
not accepting every arbitrary source fragment. That cost buys discoverable commands, stable identities, atomic failure,
and persistence that does not depend on Python import paths.
