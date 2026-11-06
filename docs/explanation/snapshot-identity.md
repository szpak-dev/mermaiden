# Snapshot identity

Persisted diagrams use registry-owned discriminators. These identify semantic types independently of Python module
paths and prevent stored data from requesting arbitrary imports.

Every supported diagram and nested object type has an identity assigned by the runtime registry. A snapshot envelope
records those identities with a schema version and JSON-safe values. Restoration parses the closed envelope, resolves
identities through the registered contract, hydrates typed state, and verifies snapshots that claim to be valid.

Restoration is strict: `restore()` accepts only the snapshot version described by the checked-in schema. Each stored
value must satisfy its registered type contract; restoration rejects incompatible data and missing required values.

Historical snapshots use the explicit `upgrade_snapshot()` operation. Adjacent migrators validate the historical
differences they own and retain original-value provenance. The upgrade service resolves the current target from the
registry, enforces loss acceptance, and validates the resulting snapshot through current persistence. It returns the
candidate with a structured change report. See [the upgrade guide](../how-to/persist-and-restore.md)
for supported versions and removal policies.
