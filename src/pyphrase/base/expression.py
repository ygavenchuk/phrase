from typing import TYPE_CHECKING, TypeVar

from pyphrase.base.ast.node import BinaryNode, ConstantNode, Node, UnaryNode
from pyphrase.base.operator import LogicalOperator, UnaryOperator

if TYPE_CHECKING:
    from pyphrase.base.compiler import BaseCompiler
    from pyphrase.base.types import LiteralValue


T = TypeVar("T")


class Expression[T]:
    __slots__ = ("_compiler_class", "_node", "_optimizer_class")

    def __init__(
        self,
        node: Node,
        compiler_class: type[BaseCompiler[T]],
    ) -> None:
        self._node = node
        self._compiler_class = compiler_class

    @staticmethod
    def _ensure_node(other: Expression[T] | LiteralValue) -> Node:
        """
        Converts input value into an AST node, if necessary

        Raises:
             TypeError: If the input value cannot be converted to a node

        Returns:
            The input value as an AST node
        """
        if isinstance(other, Expression):
            return other.node

        if isinstance(other, bool):
            return ConstantNode(other)

        raise TypeError(f"Cannot combine Expression with {type(other)}")

    def __and__(self, other: Expression[T] | LiteralValue) -> Expression[T]:
        return Expression[T](
            BinaryNode(
                left=self.node,
                operator=LogicalOperator.AND,
                right=self._ensure_node(other),
            ),
            self._compiler_class,
        )

    def __or__(self, other: Expression[T] | LiteralValue) -> Expression[T]:
        return Expression[T](
            BinaryNode(
                left=self.node,
                operator=LogicalOperator.OR,
                right=self._ensure_node(other),
            ),
            self._compiler_class,
        )

    def __rand__(self, other: Expression[T] | LiteralValue) -> Expression[T]:
        return Expression[T](
            BinaryNode(
                left=self._ensure_node(other),
                operator=LogicalOperator.AND,
                right=self.node,
            ),
            self._compiler_class,
        )

    def __ror__(self, other: Expression[T] | LiteralValue) -> Expression[T]:
        return Expression[T](
            BinaryNode(
                left=self._ensure_node(other),
                operator=LogicalOperator.OR,
                right=self.node,
            ),
            self._compiler_class,
        )

    def __invert__(self) -> Expression[T]:
        return Expression[T](
            UnaryNode(node=self.node, operator=UnaryOperator.NOT),
            self._compiler_class,
        )

    def __str__(self) -> str:
        return str(self._compiler_class().compile(self.node))

    @property
    def node(self) -> Node:
        return self._node

    def compile(self) -> T:
        return self._compiler_class().compile(self.node)
