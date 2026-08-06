# Diagram core prototype

This prototype splits the model into five independent concepts:

- **Diagram** is the immutable aggregate root and Visitor host.
- **Element** is a contained thing with a diagram-local stable ID.
- **Relation** connects element IDs but is never an element itself.
- **Constraint** is a side-effect-free Visitor that produces structured
  violations; constraints are policy, not mutation hooks.
- **Annotation** targets a typed stable reference and does not change structural
  semantics.

Dependency direction is `flowchart -> runtime -> core`. The core has no
framework or Mermaid dependency. Every runtime behavior is a frozen dataclass
service composed by `wireup`; typed dataclass fields are injection properties
and no service has a handwritten constructor. Runtime is a stateless building
environment: each operation transforms an immutable `DiagramDraft`, checks
structural invariants, and emits an immutable snapshot. Flowchart injects that
runtime service, its constraint-service set, and a Mermaid renderer service.

The design intentionally uses these patterns:

- **Visitor** for constraints and renderers (`diagram.accept(visitor)`),
- **Immutable Builder** for atomic construction without shared mutable state,
- **Facade** for the flowchart-specific building language,
- **Strategy** for replaceable rendering,
- **Aggregate/Snapshot** for publication of consistent immutable state.

Adding another diagram type should require a domain package containing its
elements, relations, annotations, constraints, builder facade, and renderer. It
must not require edits to core or runtime.
