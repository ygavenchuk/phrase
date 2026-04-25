from typing import TYPE_CHECKING, TypeVar

from phrase.base.ast.node import BinaryConstraint, ConstantNode, UnaryConstraint
from phrase.base.expression import Expression
from phrase.base.operator import BinaryOperator, Operator, UnaryOperator

if TYPE_CHECKING:
    from phrase.base.compiler import BaseCompiler
    from phrase.base.types import CollectionValue, LiteralValue, Scalar

__all__ = ("BaseField", "ConstantFactory")


T = TypeVar("T")


class BaseField[T]:
    __slots__ = ("_field",)
    _compiler_class: type[BaseCompiler[T]]

    def _binary(self, operator: Operator, value: LiteralValue) -> Expression[T]:
        if isinstance(value, Expression):
            value = value.node

        return Expression[T](
            BinaryConstraint(field=self._field, operator=operator, value=value),
            self._compiler_class,
        )

    def _unary(self, operator: Operator) -> Expression[T]:
        return Expression[T](
            UnaryConstraint(field=self._field, operator=operator),
            self._compiler_class,
        )

    def __init__(self, field: str) -> None:
        self._field = field

    def __eq__(self, other: LiteralValue) -> Expression[T]:  # type: ignore[override]
        return self._binary(BinaryOperator.EQ, other)

    def __ne__(self, other: LiteralValue) -> Expression[T]:  # type: ignore[override]
        return self._binary(BinaryOperator.NE, other)

    def __gt__(self, other: LiteralValue) -> Expression[T]:
        return self._binary(BinaryOperator.GT, other)

    def __ge__(self, other: LiteralValue) -> Expression[T]:
        return self._binary(BinaryOperator.GE, other)

    def __lt__(self, other: LiteralValue) -> Expression[T]:
        return self._binary(BinaryOperator.LT, other)

    def __le__(self, other: LiteralValue) -> Expression[T]:
        return self._binary(BinaryOperator.LE, other)

    def in_(self, values: CollectionValue) -> Expression[T]:
        return self._binary(BinaryOperator.IN, list(values))

    def is_null(self) -> Expression[T]:
        return self._unary(UnaryOperator.IS_NULL)

    def is_not_null(self) -> Expression[T]:
        return self._unary(UnaryOperator.IS_NOT_NULL)

    def not_in(self, values: CollectionValue) -> Expression[T]:
        return ~(self.in_(values))

    def between(self, low: LiteralValue, high: LiteralValue) -> Expression[T]:
        return (self >= low) & (self <= high)

    @classmethod
    def constant(cls, value: bool) -> Expression[T]:
        return Expression[T](ConstantNode(value), cls._compiler_class)

    equal = eq = __eq__
    not_equal = ne = __ne__
    greater_than = gt = __gt__
    greater_than_or_equal = ge = __ge__
    less_than = lt = __lt__
    less_than_or_equal = le = __le__


class ConstantFactory[T]:
    __slots__ = ("_compiler_class",)

    def __init__(self, compiler_class: type[BaseCompiler[T]]) -> None:
        self._compiler_class = compiler_class

    def __call__(self, value: Scalar) -> Expression[T]:
        """
        Calls the instance to create an Expression[T] object using the provided value.

        Arguments:
        value (Scalar): The scalar value to be used in the creation of the
        Expression[T].

        Returns:
        Expression[T]: An Expression[T] constructed with a constant node containing
        the given value and the associated compiler class.
        """
        return Expression[T](ConstantNode(value), self._compiler_class)

    def true(self) -> Expression[T]:
        return self(True)

    def false(self) -> Expression[T]:
        return self(False)

    def null(self) -> Expression[T]:
        return self(None)
