# Glossary

## Annotation

A typed diagram object that adds information to another object without participating as a relation endpoint.

## Application

The public Mermaiden facade. It owns diagram discovery, creation, commands, snapshots, rendering, validation, and
preview operations for callers.

## Command

A named semantic operation with a strict JSON-shaped argument contract. Commands change diagram state without exposing a
concrete feature implementation.

## Diagram description

The runtime value returned by `diagram_description()`, containing one syntax's object, placement, command, and payload
schemas.

## Diagram contract

The complete discoverable contract for one registered diagram syntax: its diagram description, command payloads,
placements, and snapshot contract identity. A mutation contract documents only the shared semantic mutation subset.

## Diagram feature

The complete registration of one supported Mermaid syntax: its model, configuration, commands, constraints, snapshot
types, and rendering templates.

## Draft

Typed and persistable diagram state that still has blocking constraints. A draft may be restored but cannot render until
it becomes valid.

## Element

A typed object contained by a diagram or another element. Elements have stable identities and may form a diagram-defined
subtree.

## Mermaid compatibility

Agreement between Mermaiden's registered configuration models and the pinned upstream Mermaid configuration schema.

## Mermaid source

Deterministic text rendered from a valid typed diagram. It is output, not Mermaiden's stored model.

## Mutation contract

The generated authority for update, move, reorder, retarget, no-op, and atomic rejection behavior across registered
diagrams.

## Render report

The result of full SVG validation. It carries the diagram ID, expected Mermaid version, SVG on success, and structured
diagnostics on failure.

## Relation

A typed diagram object whose ordered participants refer to existing elements according to diagram-specific constraints.

## Snapshot

A JSON-safe, versioned representation of diagram state using registry-owned type identities rather than Python import
paths.

## Snapshot contract identity

The registry-owned identity of the persisted contract for one diagram syntax.

## Validation report

The typed result of checking diagram constraints. Blocking diagnostics prevent commit or rendering; non-blocking results
remain available to the caller.
