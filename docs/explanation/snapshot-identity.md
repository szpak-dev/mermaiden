# Snapshot identity

Persisted diagrams outlive the Python objects that produced them. Encoding a module path and class name would turn an
internal refactor into a storage migration and would let untrusted data request arbitrary imports. Mermaiden uses
registry-owned discriminators instead.

Every supported diagram and nested object type has an identity assigned by the runtime registry. A snapshot envelope
records those identities with a schema version and JSON-safe values. Restoration parses the closed envelope, resolves
identities through the registered contract, hydrates typed state, and verifies snapshots that claim to be valid.

Versioning is strict. The package accepts the current snapshot version described by the checked-in schema and rejects
earlier or unknown versions. It does not silently reinterpret old data or fabricate missing values. A migration, when
one is intentionally designed, must therefore be explicit outside the current reader.

This boundary keeps two kinds of compatibility honest. Python package structure may change without leaking into stored
data, while a real persisted-contract change remains visible as a version decision. The stored value says what semantic
type it represents, not which implementation class happened to own it at one point in time.
