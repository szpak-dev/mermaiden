"""Compatibility names for the prototype's public abstraction layer.

The architecture uses normal Python abstract base classes and protocols.  A
custom metaclass used to live here; keeping this small alias avoids coupling
the core to metaclass magic while giving early callers a gentle migration.
"""

class Interface:
    """Deprecated spelling for a framework-free abstract contract."""
