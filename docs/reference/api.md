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

Import `DiagramCommand`, `CommandPayload`, `CommandArguments`, snapshot identity, and public exceptions directly
from `mermaiden`, alongside `Application`. The generated package reference above includes these public contracts.

## Returned data contracts

The tables below summarize values returned from `Application`. `CommandPayload`, `CommandArguments`, and
`DiagramSnapshotContractIdentity`, `SnapshotUpgradeResult`, and `SnapshotChange` are also importable directly from
`mermaiden`. The remaining implementation-owned return
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

`SnapshotUpgradeResult`
: `snapshot` is the validated current `DiagramSnapshot`; `changes` is an ordered tuple of `SnapshotChange` values.

`SnapshotChange`
: `paths` contains affected JSON Pointers, `description` explains the change, `discarded` maps original pointers to
  complete discarded values, and `requires_loss_acceptance` identifies removals requiring explicit consent.

`upgrade_snapshot(payload, *, allow_loss=False)` upgrades v6–v11 snapshots to v12. A valid current snapshot returns
unchanged JSON values and no changes. The operation preserves its input and does not render or perform I/O.

### Full render validation

`MermaidRenderReport`
: `diagram_id`, `mermaid_version`, `mermaid_cli_version`, `svg`, `diagnostics`, and computed `success`.

`MermaidRenderDiagnostic`
: `code`, `message`, and `details` describe one renderer failure.

`svg` is non-empty only on success. Diagnostic codes distinguish invalid typed state, source-generation failure,
unavailable or mismatched CLI, timeout, renderer failure, and missing, empty, or syntax-error SVG output.

## Failure behavior

Unknown diagram or command contract
: Diagram lookup raises `UnknownDiagram`; command discovery raises `UnknownCatalogCommand` for an unknown command.

Unsupported operation or invalid command arguments
: `apply()` and `execute()` raise `UnknownCommand` for unsupported operations and `InvalidCommandArguments` for
  invalid arguments. Both derive from `ApplicationError`.

Rejected state change
: A command or final batch that violates diagram constraints raises `ChangeRejected`. Rejected commands preserve the
  pre-command snapshot; failed batches restore their complete original snapshot.

Malformed batch envelope
: `apply_batch()` raises `InvalidBatchCommand` when an item lacks a string `operation` or mapping `arguments`. After the envelope
  is accepted, command and constraint failures follow the behavior above.

Invalid snapshot or source render
: `snapshot_contract_identity()` raises `SnapshotError` for an unregistered snapshot contract. Malformed snapshots
  and invalid persisted state raise `SnapshotError`. `render()` raises
  `MermaidRenderFailure` for invalid diagram state. `validate_render()` returns a failed `MermaidRenderReport` for
  expected diagram, CLI, timeout, and SVG failures.

Invalid PNG export or renderer failure
: `render_png()` raises `PngExportOptionsError` for invalid scale or background options and `MermaidRenderFailure`
  for diagram or renderer failures. Its `code`, `message`, and `details` identify the failure.

Invalid snapshot upgrade or unaccepted loss
: `upgrade_snapshot()` raises `SnapshotUpgradeError`, a public `SnapshotError` subclass. `paths` identifies affected
  locations using JSON Pointers; `changes` carries proposed changes when loss is refused. There is no partial-success
  snapshot. `allow_loss=True` permits only documented removals and never permits malformed input.

Closed application handle
: Diagram operations after `close()` raise `ApplicationClosed`. Repeated `close()` calls are harmless.
