# Flowchart semantic vocabulary

This document proposes the domain surface that should exist before the new
flowchart renderer is implemented. It deliberately models flowchart meaning,
not the complete Mermaid presentation API.

## Boundary

Core remains independent of Mermaid and Jinja. The flowchart domain describes
which elements exist and how they are related. The MMD rendering package decides
how those concepts are written and displayed.

Mermaid's default theme supplies colors, borders, typography, spacing, and
arrow appearance. The first renderer will not emit a palette or style rules.

## Elements

All nodes have a stable diagram-local ID and a required human-readable label.
The initial vocabulary is:

- `FlowNode`: a general node when no narrower semantic type applies;
- `Start`: the entry point of a flow;
- `End`: a terminal point;
- `Action`: an operation or process step;
- `Decision`: a branch selected by conditions;
- `InputOutput`: data entering or leaving the flow;
- `DataStore`: persisted data;
- `Document`: a document produced or consumed by the flow;
- `Subprocess`: a named process whose details are outside the current flow;
- `Junction`: a merge or split point without an operation of its own;
- `FlowGroup`: a recursively nested container of flowchart elements.

These are semantic types, not user-selectable Mermaid shapes. For example,
`Decision` is a decision regardless of whether a future renderer draws it as a
diamond or uses another notation.

`FlowGroup.elements` is the sole source of containment truth. The model will not
maintain a second collection of child IDs.

### Default MMD representation

Each semantic type receives one conventional representation in its Jinja
snippet:

| Element | Default representation |
| --- | --- |
| `FlowNode` | rectangle |
| `Start` | start circle |
| `End` | terminal/double circle |
| `Action` | process rectangle |
| `Decision` | diamond |
| `InputOutput` | input/output parallelogram |
| `DataStore` | database cylinder |
| `Document` | document |
| `Subprocess` | framed process |
| `Junction` | junction circle |
| `FlowGroup` | subgraph |

Callers do not pass raw Mermaid shape tokens. Changing a representation is a
template concern and does not change the domain type.

## Relations

The initial vocabulary has two binary, directed relations:

- `Flow`: connects a source element to a target element and may have an
  optional label;
- `ConditionalFlow`: connects a source to a target using one required,
  non-blank condition.

A conditional flow has one displayed condition. It does not have separate
`label` and `condition` strings. The aggregate API is therefore:

```python
add_flow(id, source_id, target_id, label="")
add_conditional_flow(id, source_id, target_id, condition)
```

The condition can occupy the inherited relation label internally while the
public flowchart vocabulary exposes it as `condition`.

Flows may connect flow nodes, including nodes inside groups. Groups themselves
are not flow endpoints in this iteration.

## Minimal annotation

`Note` remains the only annotation in the first iteration. It contains typed
text and targets one or more elements. Relation-targeted notes are deferred
until a faithful MMD representation is chosen.

The concrete `Note` should expose `text` directly. Templates should not read an
untyped key such as `note.data["text"]`.

## Direction

The existing flowchart and group directions remain. Top-down is the default.
Direction affects layout but is fundamental enough to flowchart structure to
keep in the domain.

Changing the root direction through the aggregate needs a dedicated operation;
it must not be implemented as arbitrary Mermaid configuration.

## Template dispatch

Accepted flowchart values receive stable semantic `kind` discriminators. Jinja
uses them to select snippets. Renderer Python code must not contain Mermaid
node syntax or an `isinstance` dispatch chain.

The expected initial snippets are:

```text
elements/flow_node
elements/start
elements/end
elements/action
elements/decision
elements/input_output
elements/data_store
elements/document
elements/subprocess
elements/junction
elements/flow_group
relations/flow
relations/conditional_flow
annotations/note
```

This is intentionally a small amount of template duplication. Each file owns
the complete MMD representation of one semantic concept, so adding an element
does not require editing renderer logic.

## Validation ownership

Flowchart constraints validate:

- membership of elements, relations, and notes;
- unique IDs and valid references;
- binary flow endpoints;
- flow endpoints are nodes rather than groups;
- exactly one start;
- start, end, decision, junction, and normal-node degree rules;
- every node is reachable from the start;
- every decision branch is a conditional flow;
- decision conditions are non-blank and unique;
- notes have non-blank text and valid element targets.

Normal flows may be unlabeled. Requiring labels on every relation would reject
ordinary flowchart arrows, so the shared label constraint must distinguish
required element labels from optional relation labels.

Templates serialize state that has already passed blocking structural
constraints. They handle quoting and escaping, not domain validation.

## Deferred presentation features

The following are not part of the initial domain or renderer:

- the full Mermaid shape catalog;
- caller-selected shapes;
- CSS classes, inline styles, and style definitions;
- custom color palettes and themes;
- icon and image nodes;
- Markdown labels;
- link line variants, endpoint decorations, curves, and animation;
- click interactions and callbacks;
- comments and accessibility directives;
- arbitrary Mermaid initialization configuration;
- JSON Schema generation;
- SVG or PNG rendering.

These can be added later as separate, reviewable capabilities. They must not
complicate the element/relation model preemptively.

## Decisions requested

Implementation begins after agreement that:

1. the listed semantic elements are sufficient for the first complete model;
2. normal flow labels are optional;
3. conditional flows expose one required condition;
4. notes initially target elements only;
5. Mermaid default styling is sufficient for the first renderer.
