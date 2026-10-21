# Public Python API

Create the public facade with `Application.create()` and use it as a context manager. The direct `Application(scope)`
constructor is an implementation composition seam, not the consumer entry point.

## Application facade

The generated facade reference follows `mermaiden.__all__`. A strict documentation build fails if that export is empty,
duplicated, or unresolved.

```{eval-rst}
.. automodule:: mermaiden
   :members:
   :imported-members:
   :exclude-members: __init__
   :member-order: bysource
   :show-inheritance:
```

## Command input and errors

`mermaiden.domain` publishes the typed `DiagramCommand`, validating `CommandPayload`, validated `CommandArguments`,
snapshot identity, and public application errors used with the facade.

```{eval-rst}
.. automodule:: mermaiden.domain
   :members:
   :imported-members:
   :member-order: bysource
```

## Returned data contracts

The tables below summarize values returned from `Application`. `CommandPayload`, `CommandArguments`, and
`DiagramSnapshotContractIdentity` are also importable from `mermaiden.domain`. The remaining implementation-owned return
types are observed through the documented fields and properties rather than imported or constructed by callers.

### Discovery

`DiagramInfo`
: `id`, `name`, `diagram_type`, `config_key`, and `schema_definition` identify one registered syntax.

`DiagramDescription`
: `id`, `name`, `elements`, `relations`, `annotations`, `placements`, and `commands` expose its schemas.

`CommandPayload`
: `schema()` returns the JSON-shaped input schema; `validate(arguments)` returns `CommandArguments`.

`CommandArguments`
: `values` contains converted typed values; `invocation` contains the command-ready mapping.

### Mutation and validation

`Violation`
: `code`, `message`, `path`, and `level` describe one blocking or advisory result.

`ValidationReport`
: `violations`, `blocking`, `advisory`, `can_commit`, and `is_valid` describe the complete state check.

`ChangeReport`
: `operation`, `before`, `after`, `accepted`, `removed`, `introduced`, `resolved`, and `current` describe one command.

`DiagramObjectReference`
: `kind` and `id` identify an element, relation, or annotation removed by a command.

`apply_batch()` returns a `ValidationReport` for the final atomic state. `configure` returns `None`; every other catalog
command returns a `ChangeReport`, including accepted no-ops that preserve the snapshot.

### Persistence

`DiagramSnapshot`
: `version`, `kind`, `draft`, `configuration`, `elements`, `relations`, `annotations`, and `properties`; `to_dict()`
  returns the JSON-safe envelope.

`DiagramSnapshotContractIdentity`
: `kind`, `snapshot_version`, and `registry_fingerprint` identify the accepted persisted contract.

### Full render validation

`MermaidRenderReport`
: `diagram_id`, `mermaid_version`, `mermaid_cli_version`, `svg`, `diagnostics`, and computed `success`.

`MermaidRenderDiagnostic`
: `code`, `message`, and `details` describe one renderer failure.

`svg` is non-empty only on success. Diagnostic codes distinguish invalid typed state, source-generation failure,
unavailable or mismatched CLI, timeout, renderer failure, and missing, empty, or syntax-error SVG output.

## Failure behavior

Unknown diagram or command contract
: `diagram_info()`, `create_diagram()`, `diagram_description()`, and `command_payload()` raise `KeyError` for an unknown
  diagram or command name.

Unsupported operation or invalid command arguments
: `apply()` and `execute()` raise the public `UnknownCommand`, which is an `ApplicationError` and `RuntimeError`.

Rejected state change
: A command or final batch that violates diagram constraints raises `RuntimeError`. Rejected commands preserve the
  pre-command snapshot; failed batches restore their complete original snapshot.

Malformed batch envelope
: `apply_batch()` raises `ValueError` when an item lacks a string `operation` or mapping `arguments`. After the envelope
  is accepted, command and constraint failures follow the behavior above.

Invalid snapshot or source render
: `snapshot_contract_identity()` raises `RuntimeError` for an unregistered snapshot contract. `restore()` and `render()`
  raise `RuntimeError` when their typed state cannot be accepted. `validate_render()` instead returns a failed
  `MermaidRenderReport` for expected diagram, CLI, timeout, and SVG failures.

Closed application handle
: Every operation after `close()` raises `RuntimeError`.
