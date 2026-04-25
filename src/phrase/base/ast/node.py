"""
Contains AST Nodes (Performance & AST Optimization)
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from phrase.base.operator import Operator
    from phrase.base.types import Scalar


@dataclass(frozen=True, slots=True)
class Node:
    pass


@dataclass(frozen=True, slots=True)
class BinaryConstraint(Node):
    field: str
    operator: Operator
    value: Any


@dataclass(frozen=True, slots=True)
class UnaryConstraint(Node):
    field: str
    operator: Operator


@dataclass(frozen=True, slots=True)
class BinaryNode(Node):
    left: Node
    operator: Operator
    right: Node


@dataclass(frozen=True, slots=True)
class UnaryNode(Node):
    node: Node
    operator: Operator


@dataclass(frozen=True, slots=True)
class ConstantNode(Node):
    value: Scalar
