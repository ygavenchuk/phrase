"""
Common SQL Dialect Components Module.

This module provides the foundational infrastructure for various SQL dialects.
Its primary purpose is to consolidate shared logic and standard ANSI SQL
behaviors, preventing code duplication across specific dialect implementations
(e.g., PostgreSQL, MySQL, SQLite, MSSQL).

Core Objectives:
    * Standardization: Implements the default ANSI SQL rendering logic for
      operators and literals.
    * Extensibility: Provides a base `SQLRenderer` class that specific dialects
      can subclass to override only the parts of the syntax that differ.
    * Consistency: Ensures that basic data types (strings, numbers, nulls) are
      handled uniformly unless a dialect-specific requirement exists.

Functional Features:
    * SQLRenderer: A base class containing a comprehensive mapping of binary
      and unary operators to their standard SQL string representations.
    * Literal Rendering: Intelligent conversion of Python primitives (bool,
      str, int, float, None) and collections (list, tuple) into SQL-compliant
      constants.
    * Shared Operator Mapping: Default support for standard operations like
      equality, comparison, LIKE patterns, and NULL checks.

Architecture:
    This module acts as a "Default" layer. Specific dialects should import
    the classes defined here and extend them to implement dialect-specific
    features such as identifier quoting (backticks vs. double quotes) or
    special operators (e.g., ILIKE in Postgres).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from pyphrase.base.ast.node import (
    BinaryConstraint,
    BinaryNode,
    ConstantNode,
    Node,
    UnaryConstraint,
    UnaryNode,
)
from pyphrase.base.ast.rules import TransformationRule
from pyphrase.base.compiler import BaseCompiler
from pyphrase.base.factory import BaseField, ConstantFactory
from pyphrase.base.operator import (
    BinaryOperator,
    LikeOperator,
    Operator,
    UnaryOperator,
)
from pyphrase.base.renderer import Renderer

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyphrase.base.expression import Expression
    from pyphrase.base.types import LiteralValue, Scalar


class LikeInversionRule(TransformationRule):
    __slots__ = ()

    def apply(self, node: Node) -> Node:
        # In InversionRule.apply:
        match node:
            case UnaryNode(
                BinaryConstraint(field, LikeOperator.LIKE, value), UnaryOperator.NOT
            ):
                return BinaryConstraint(field, LikeOperator.NOT_LIKE, value)

            case UnaryNode(
                BinaryConstraint(field, LikeOperator.NOT_LIKE, value),
                UnaryOperator.NOT,
            ):
                return BinaryConstraint(field, LikeOperator.LIKE, value)

        return node


class ILikeInversionRule(TransformationRule):
    __slots__ = ()

    def apply(self, node: Node) -> Node:
        # In InversionRule.apply:
        match node:
            case UnaryNode(
                BinaryConstraint(field, LikeOperator.ILIKE, value), UnaryOperator.NOT
            ):
                return BinaryConstraint(field, LikeOperator.NOT_ILIKE, value)

            case UnaryNode(
                BinaryConstraint(field, LikeOperator.NOT_ILIKE, value),
                UnaryOperator.NOT,
            ):
                return BinaryConstraint(field, LikeOperator.ILIKE, value)

        return node


class SQLRenderer(Renderer[str]):
    __slots__ = ()

    _mapping: ClassVar[Mapping[Operator, str]] = MappingProxyType(
        {
            BinaryOperator.EQ: "=",
        }
    )

    @staticmethod
    def _render_datetime(value: datetime) -> str:
        if value.microsecond:
            return f"'{value.isoformat(sep=' ', timespec='milliseconds')}'"

        return f"'{value.isoformat(sep=' ')}'"

    @staticmethod
    def _escape_string(literal: str) -> str:
        escaped_literal = literal.replace("'", "''")
        return f"'{escaped_literal}'"

    @staticmethod
    def _render_boolean(value: bool) -> str:
        return "TRUE" if value else "FALSE"

    @staticmethod
    def _render_null() -> str:
        return "NULL"

    @staticmethod
    def _render_string(value: Scalar) -> str:
        return str(value)

    def render_field(self, field: str) -> str:
        # SQLite uses double quotes for identifiers
        return f'"{field}"'

    def render_operator(self, operator: Operator) -> str:
        # Map generic operators to SQLite specific ones if needed
        return self._mapping.get(operator, str(operator))

    def render_literal(self, literal: LiteralValue) -> str:
        if isinstance(literal, (list, tuple, set)):
            elements = ", ".join(self.render_literal(item) for item in literal)
            return f"({elements})"

        if isinstance(literal, datetime):
            return self._render_datetime(literal)

        if isinstance(literal, str):
            # Simple escaping for SQLite
            return self._escape_string(literal)

        if isinstance(literal, bool):
            return self._render_boolean(literal)

        if literal is None:
            return self._render_null()

        return self._render_string(literal)


class SQLCompiler(BaseCompiler[str]):
    __slots__ = ()

    renderer_class = SQLRenderer
    optimization_rules = (
        *BaseCompiler.optimization_rules,
        LikeInversionRule,
    )

    def _render(self, node: Node) -> str:
        match node:
            case BinaryConstraint(field, operator, Node() as value_node):
                return (
                    f"{self.renderer.render_field(field)} "
                    f"{self.renderer.render_operator(operator)} "
                    f"{self._render(value_node)}"
                )

            case BinaryConstraint(field, operator, value):
                return (
                    f"{self.renderer.render_field(field)} "
                    f"{self.renderer.render_operator(operator)} "
                    f"{self.renderer.render_literal(value)}"
                )

            case UnaryConstraint(field, operator):
                return (
                    f"{self.renderer.render_field(field)} "
                    f"{self.renderer.render_operator(operator)}"
                )

            case BinaryNode(left, operator, right):
                return (
                    f"({self.compile(left)}) "
                    f"{self.renderer.render_operator(operator)} "
                    f"({self.compile(right)})"
                )

            case UnaryNode(node, operator):
                return f"{self.renderer.render_operator(operator)} ({self.compile(node)})"

            case ConstantNode(value):
                return str(self.renderer.render_literal(value))
            case _:
                raise NotImplementedError(
                    f"No render rule for node type: {type(node).__name__}"
                )


T = TypeVar("T")


class ILikeableMixin(ABC, Generic[T]):
    __slots__ = ()

    @abstractmethod
    def _binary(self, operator: Operator, value: LiteralValue) -> Expression[T]: ...

    def ilike(self, pattern: str) -> Expression[T]:
        return self._binary(LikeOperator.ILIKE, pattern)

    def not_ilike(self, pattern: str) -> Expression[T]:
        return self._binary(LikeOperator.NOT_ILIKE, pattern)


class F(BaseField[str]):
    """Field factory specialized for SQLite."""

    __slots__ = ()

    _compiler_class = SQLCompiler

    def like(self, pattern: str) -> Expression[str]:
        return self._binary(LikeOperator.LIKE, pattern)

    def not_like(self, pattern: str) -> Expression[str]:
        return self._binary(LikeOperator.NOT_LIKE, pattern)


C = ConstantFactory(compiler_class=SQLCompiler)
