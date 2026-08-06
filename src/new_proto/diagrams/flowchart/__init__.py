"""Flowchart aggregate and its domain vocabulary."""

from . import constraints as _constraints
from .annotations import Note
from .diagram import Flowchart
from .elements import Action, Decision, Direction, End, FlowGroup, FlowNode, Start
from .relations import ConditionalFlow, Flow

_DISCOVERY_MODULES = (_constraints,)

__all__ = [
    "Action",
    "ConditionalFlow",
    "Decision",
    "Direction",
    "End",
    "Flow",
    "FlowGroup",
    "FlowNode",
    "Flowchart",
    "Note",
    "Start",
]
