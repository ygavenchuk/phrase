"""
MongoDB Query Document Implementation.

Unlike SQL-based dialects, this module produces BSON-compliant dictionaries
used by MongoDB for filtering. It maps standard expressions to MongoDB
query operators (e.g., $eq, $gt, $and).

Specifics:
    * Output Format: Returns Python dictionaries instead of SQL strings.
    * Operators: Translates BinaryOperator.LIKE to MongoDB's `$regex`.
    * Structure: Nesting logic handles MongoDB's characteristic prefix
      notation for logical operators like `$and` and `$or`.
"""

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, ClassVar

from phrase.base.ast.node import (
    BinaryConstraint,
    BinaryNode,
    ConstantNode,
    UnaryConstraint,
    UnaryNode,
)
from phrase.base.compiler import BaseCompiler
from phrase.base.factory import BaseField, ConstantFactory
from phrase.base.operator import (
    BinaryOperator,
    LikeOperator,
    Operator,
    UnaryOperator,
)
from phrase.base.renderer import Renderer
from phrase.base.types import LiteralValue

if TYPE_CHECKING:
    from collections.abc import Mapping

    from phrase.base.ast.node import Node
    from phrase.base.expression import Expression


type TMongoRendered = dict[str, Any] | LiteralValue


class MongoRenderer(Renderer[LiteralValue]):
    __slots__ = ()
    _mapping: ClassVar[Mapping[Operator, str]] = MappingProxyType(
        {
            BinaryOperator.EQ: "$eq",
            BinaryOperator.NE: "$ne",
            BinaryOperator.GT: "$gt",
            BinaryOperator.GE: "$gte",
            BinaryOperator.LT: "$lt",
            BinaryOperator.LE: "$lte",
            BinaryOperator.IN: "$in",
            LikeOperator.LIKE: "$regex",  # SQL's LIKE -> Mongo's $regex
        }
    )

    def render_field(self, field: str) -> str:
        # Mongo's field's names are just dictionary keys
        return field

    def render_operator(self, operator: Operator) -> str:
        return self._mapping.get(operator, f"${operator.name.lower()}")

    def render_literal(self, literal: LiteralValue) -> LiteralValue:
        return literal


class MongoCompiler(BaseCompiler[TMongoRendered]):
    renderer_class = MongoRenderer

    def _render(self, node: Node) -> TMongoRendered:
        mongo_not = self.renderer.render_operator(UnaryOperator.NOT)
        mongo_ne = self.renderer.render_operator(BinaryOperator.NE)

        match node:
            #  IS_NULL
            case UnaryConstraint(field, UnaryOperator.IS_NULL):
                return {self.renderer.render_field(field): None}

            case UnaryConstraint(field, UnaryOperator.IS_NOT_NULL):
                return {self.renderer.render_field(field): {mongo_ne: None}}

            # EQ
            case BinaryConstraint(field, BinaryOperator.EQ, ConstantNode(value) | value):
                return {self.renderer.render_field(field): value}

            # Binary operators: !=, >, <, $in
            case BinaryConstraint(field, operator, ConstantNode(value) | value):
                mongo_operator = self.renderer.render_operator(operator)
                return {self.renderer.render_field(field): {mongo_operator: value}}

            # logical operators
            case BinaryNode(left, operator, right):
                # (AND -> $and, OR -> $or)
                mongo_operator = self.renderer.render_operator(operator)
                return {mongo_operator: [self._render(left), self._render(right)]}

            case UnaryNode(
                BinaryConstraint(field, LikeOperator.LIKE, value), UnaryOperator.NOT
            ):
                mongo_like = self.renderer.render_operator(LikeOperator.LIKE)
                return {
                    self.renderer.render_field(field): {mongo_not: {mongo_like: value}}
                }

            case ConstantNode(value):
                return self.renderer.render_literal(value)

            case _:
                raise NotImplementedError(
                    f"MongoCompiler: No rule for node type '{type(node).__name__}'. "
                    f"Node content: {node}"
                )


class F(BaseField[TMongoRendered]):
    """Field factory specialized for SQLite."""

    __slots__ = ()

    _compiler_class = MongoCompiler

    def like(self, pattern: str) -> Expression[TMongoRendered]:
        return self._binary(LikeOperator.LIKE, pattern)

    def not_like(self, pattern: str) -> Expression[TMongoRendered]:
        return ~self._binary(LikeOperator.LIKE, pattern)


C = ConstantFactory(compiler_class=MongoCompiler)
