"""
Implements various transformation rules for optimizing and transforming
abstract syntax tree (AST) nodes.

This module provides a set of transformation rules that can be applied to
AST nodes to perform logical optimizations and transformations such as
DeMorgan's laws, constant folding, double negation elimination, and
null value optimizations. These rules operate on nodes and return
transformed nodes where applicable.

Classes:
    - `TransformationRule`: Protocol defining the structure for transformation rules.
    - `DeMorganRule`: Applies DeMorgan's laws to nodes.
    - `DoubleNegationRule`: Simplifies expressions with double negations.
    - `InvertBinaryRule`: Inverts binary operators within nodes.
    - `ConstantFoldingRule`: Performs constant folding on nodes.
    - `InvertUnaryRule`: Inverts unary operators within nodes.
    - `NullOptimizationRule`: Optimizes nodes with null checks.
"""

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Protocol, cast

from pyphrase.base.ast.node import (
    BinaryConstraint,
    BinaryNode,
    ConstantNode,
    Node,
    UnaryConstraint,
    UnaryNode,
)
from pyphrase.base.operator import (
    BinaryOperator,
    LogicalOperator,
    Operator,
    UnaryOperator,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class TransformationRule(Protocol):
    """
    Defines the TransformationRule protocol for applying transformations to nodes.

    This protocol outlines the structure for creating transformation rules that
    can be applied to nodes. Implementations of this protocol should provide a specific
    transformation logic by defining the `apply` method. The primary use of this
    structure is to standardize the application of rules for consistent handling
    of nodes in a processing system.

    Methods:
        apply(node: Node) -> Node:
            Describes the transformation logic to be applied to a node.
    """

    def apply(self, node: Node) -> Node: ...


class DeMorganRule(TransformationRule):
    """
    Represents the De Morgan transformation rule for logical expressions.

    This class is used to apply De Morgan's laws, transforming logical expressions by
    rewriting negated conjunctions (AND) as disjunctions (OR) of negations, and vice
    versa. It operates specifically on Abstract Syntax Trees (AST) composed of nodes,
    and is intended to simplify or reformulate logical statements.
    """

    __slots__ = ()

    def apply(self, node: Node) -> Node:
        match node:
            case UnaryNode(
                BinaryNode(left, LogicalOperator.AND, right), UnaryOperator.NOT
            ):
                return BinaryNode(
                    UnaryNode(left, UnaryOperator.NOT),
                    LogicalOperator.OR,
                    UnaryNode(right, UnaryOperator.NOT),
                )
            case UnaryNode(
                BinaryNode(left, LogicalOperator.OR, right), UnaryOperator.NOT
            ):
                return BinaryNode(
                    UnaryNode(left, UnaryOperator.NOT),
                    LogicalOperator.AND,
                    UnaryNode(right, UnaryOperator.NOT),
                )

        return node


class DoubleNegationRule(TransformationRule):
    """
    Handles the transformation of double negation expressions.

    This rule is designed to optimize or simplify logical expressions by
    applying the double negation elimination principle. It works by detecting
    patterns where a negation operator has been applied twice consecutively
    to the same operand and reduces it to the simpler form.
    """

    __slots__ = ()

    def apply(self, node: Node) -> Node:
        match node:
            case UnaryNode(UnaryNode(inner, UnaryOperator.NOT), UnaryOperator.NOT):
                return inner

        return node


class InvertBinaryRule(TransformationRule):
    """
    Represents a transformation rule for inverting binary operations.

    This class defines a specific rule for transforming binary operators
    into their logical complements within a unary operation context. It is
    designed to match nodes in a specific form and apply transformations
    based on a predefined mapping of binary operators.

    Supported Operators:
        - `!=`;
        - `==`;
        - `<=`;
        - `<`;
        - `>=`;
        - `>`;
        - `not in`;
        - `in`;

    """

    __slots__ = ()

    _map: ClassVar[Mapping[Operator, Operator]] = MappingProxyType(
        {
            BinaryOperator.EQ: BinaryOperator.NE,
            BinaryOperator.NE: BinaryOperator.EQ,
            BinaryOperator.GT: BinaryOperator.LE,
            BinaryOperator.GE: BinaryOperator.LT,
            BinaryOperator.LT: BinaryOperator.GE,
            BinaryOperator.LE: BinaryOperator.GT,
            BinaryOperator.IN: BinaryOperator.NOT_IN,
            BinaryOperator.NOT_IN: BinaryOperator.IN,
        }
    )

    def apply(self, node: Node) -> Node:
        match node:
            case UnaryNode(BinaryConstraint(field, operator, value), UnaryOperator.NOT):
                if new_operator := cast("BinaryOperator", self._map.get(operator)):
                    return BinaryConstraint(field, new_operator, value)

        return node


class ConstantFoldingRule(TransformationRule):
    """
    Defines a rule for performing constant folding transformations on a syntax tree.

    Constant folding is an optimization technique where constant expressions are
    evaluated and simplified at compile time. This class matches specific patterns
    in a node tree, where constant values and logical operators are involved, and
    simplifies them into their reduced forms. The purpose of this transformation
    rule is to improve the efficiency of the code by reducing redundant
    computation during runtime.
    """

    __slots__ = ()

    def apply(self, node: Node) -> Node:
        match node:
            # NOT True -> False
            case UnaryNode(ConstantNode(value), UnaryOperator.NOT):
                return ConstantNode(not value)

            # True AND X -> X
            case BinaryNode(ConstantNode(True), LogicalOperator.AND, right):
                return right

            # X AND True -> X
            case BinaryNode(left, LogicalOperator.AND, ConstantNode(True)):
                return left

            # False AND X -> False
            case BinaryNode(ConstantNode(False), LogicalOperator.AND, _):
                return ConstantNode(False)

            # X AND False -> False
            case BinaryNode(_, LogicalOperator.AND, ConstantNode(False)):
                return ConstantNode(False)

            # similarly for OR...
            # True OR X -> True
            case BinaryNode(ConstantNode(True), LogicalOperator.OR, _):
                return ConstantNode(True)

            # X OR True -> True
            case BinaryNode(_, LogicalOperator.OR, ConstantNode(True)):
                return ConstantNode(True)

            # False OR X -> X
            case BinaryNode(ConstantNode(False), LogicalOperator.OR, right):
                return right

            # X OR False -> X
            case BinaryNode(left, LogicalOperator.OR, ConstantNode(False)):
                return left

        return node


class InvertUnaryRule:
    """
    Class for applying an invert unary rule to a node.

    This class provides functionality to transform a node in a specific way by inverting
    unary operators under certain conditions. It uses a predefined mapping of unary
    operators to their inverses. This can be useful for logical transformations or
    simplifications in an abstract syntax tree (AST) context.

    Supported Operators:
        - `IS NULL`;
        - `IS NOT NULL`;
    """

    __slots__ = ()

    _map: ClassVar[Mapping[Operator, Operator]] = MappingProxyType(
        {
            UnaryOperator.IS_NULL: UnaryOperator.IS_NOT_NULL,
            UnaryOperator.IS_NOT_NULL: UnaryOperator.IS_NULL,
        }
    )

    def apply(self, node: Node) -> Node:
        match node:
            case UnaryNode(UnaryConstraint(field, operator), UnaryOperator.NOT):
                if new_operator := cast("UnaryOperator", self._map.get(operator)):
                    return UnaryConstraint(field, new_operator)
        return node


class NullOptimizationRule(TransformationRule):
    """
    Represents a transformation rule that simplifies binary constraints involving
    None or null-like values into equivalent unary constraints.

    This class implements a specialized transformation rule within the context of
    query optimization or constraint rewriting. Its primary purpose is to detect
    binary constraints in the form of equality (`==`) or inequality (`!=`) with
    `None` or a null-like constant and simplify them into suitable unary constraints
    (`IS NULL` or `IS NOT NULL`). This simplifies the representation and often
    improves overall processing efficiency.
    """

    __slots__ = ()

    def apply(self, node: Node) -> Node:
        match node:
            case BinaryConstraint(field, BinaryOperator.EQ, None):
                return UnaryConstraint(field, UnaryOperator.IS_NULL)

            # `F("field") == C.null()`
            case BinaryConstraint(field, BinaryOperator.EQ, ConstantNode(None)):
                return UnaryConstraint(field, UnaryOperator.IS_NULL)

            # `F("field") != C.null()`
            case BinaryConstraint(field, BinaryOperator.NE, ConstantNode(None)):
                return UnaryConstraint(field, UnaryOperator.IS_NOT_NULL)

            case BinaryConstraint(field, BinaryOperator.NE, None):
                return UnaryConstraint(field, UnaryOperator.IS_NOT_NULL)
        return node
