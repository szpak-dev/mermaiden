# Snapshot identity

Persisted diagrams use registry-owned discriminators. These identify semantic types independently of Python module
paths and prevent stored data from requesting arbitrary imports.

Every supported diagram and nested object type has an identity assigned by the runtime registry. A snapshot envelope
records those identities with a schema version and JSON-safe values. Restoration parses the closed envelope, resolves
identities through the registered contract, hydrates typed state, and verifies snapshots that claim to be valid.

Versioning is strict. The package accepts only the snapshot version described by the checked-in schema. Each stored
value must satisfy its registered type contract; restoration rejects incompatible data and missing required values.
