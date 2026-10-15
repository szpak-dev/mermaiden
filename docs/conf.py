from importlib import import_module

from sphinx.errors import ConfigError

project = "Mermaiden"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_external_toc",
]

source_suffix = {".md": "markdown"}
root_doc = "index"
external_toc_path = "_toc.yml"
external_toc_exclude_missing = False

autodoc_typehints = "description"
autodoc_class_signature = "separated"
nitpicky = True
nitpick_ignore = [
    ("py:class", "collections.abc.Mapping"),
    ("py:class", "collections.abc.Sequence"),
    ("py:class", "mermaiden.core.domain.ChangeReport"),
    ("py:class", "mermaiden.core.domain.CommandPayload"),
    ("py:class", "mermaiden.core.domain.Diagram"),
    ("py:class", "mermaiden.core.domain.DiagramCommand"),
    ("py:class", "mermaiden.core.domain.DiagramSnapshotContractIdentity"),
    ("py:class", "mermaiden.core.domain.ValidationReport"),
    ("py:class", "mermaiden.diagrams.catalog.models.DiagramDescription"),
    ("py:class", "mermaiden.diagrams.domain.DiagramInfo"),
    ("py:class", "mermaiden.diagrams.domain.DiagramModel"),
    ("py:class", "mermaiden.mermaid.validation.domain.MermaidRenderReport"),
    ("py:class", "mermaiden.runtime.snapshot.domain.DiagramSnapshot"),
    ("py:class", "pathlib.Path"),
    ("py:class", "wireup.ioc.container.sync_container.ScopedSyncContainer"),
]

myst_enable_extensions = ["colon_fence", "deflist"]
suppress_warnings = ["toc.not_included"]

exclude_patterns = ["_build"]
html_theme = "furo"
html_theme_options = {
    "source_repository": "https://github.com/szpak-dev/mermaiden/",
    "source_branch": "main",
    "source_directory": "docs/",
}

public_api = import_module("mermaiden")
exports = tuple(public_api.__all__)
if not exports:
    raise ConfigError("mermaiden.__all__ must publish at least one name")
if len(exports) != len(set(exports)):
    raise ConfigError("mermaiden.__all__ must contain unique names")
missing_exports = tuple(name for name in exports if not hasattr(public_api, name))
if missing_exports:
    raise ConfigError(f"mermaiden.__all__ contains unresolved names: {missing_exports!r}")
