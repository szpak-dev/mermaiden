"""Service composition for the default Diagram aggregate.

Import this module for Wireup discovery. Runtime collaborators are deliberately
not part of its public API; consumers resolve the core ``Diagram`` interface.
"""

from . import constraints as _constraints
from . import diagrams as _diagrams

_DISCOVERY_MODULES = (_constraints, _diagrams)

__all__: list[str] = []
