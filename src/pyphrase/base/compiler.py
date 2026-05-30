"""
Basic compiler
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from pyphrase.base.ast.optimizer import ASTOptimizer
from pyphrase.base.ast.rules import (
    ConstantFoldingRule,
    DeMorganRule,
    DoubleNegationRule,
    InvertBinaryRule,
    InvertUnaryRule,
    NullOptimizationRule,
    TransformationRule,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyphrase.base.ast.node import Node
    from pyphrase.base.renderer import Renderer


__all__ = ("BaseCompiler",)


T = TypeVar("T")


class BaseCompiler(ABC, Generic[T]):
    """
    A generic base class for compilers that use AST optimization and custom rendering.

    This abstract base class provides the structure and foundation for compilers that
    transform AST (Abstract Syntax Tree) nodes into specific output representations.
    It includes facilities for optimization of the AST using predefined transformation
    rules and rendering of the optimized nodes using a renderer. Subclasses are required
    to implement rendering logic specific to their use cases by overriding the `_render`
    method.
    """

    __slots__ = ("_renderer",)

    optimization_rules: Iterable[type[TransformationRule]] = (
        DoubleNegationRule,
        DeMorganRule,
        InvertUnaryRule,
        InvertBinaryRule,
        ConstantFoldingRule,
        NullOptimizationRule,
    )

    renderer_class: type[Renderer[T]]

    def __init__(self) -> None:
        self._renderer: Renderer[T] | None = None

    @property
    def renderer(self) -> Renderer[T]:
        """
        Returns the renderer instance for the associated class. If the renderer
        instance is not already initialized, it will be created using the
        `renderer_class` associated with the current class.



        Returns
        -------
        Renderer[T]
            The renderer instance for the current class.
        """
        if self._renderer is None:
            self._renderer = self.renderer_class()

        assert self._renderer is not None  # for PyCharm
        return self._renderer

    def compile(self, node: Node) -> T:
        optimizer = ASTOptimizer([rule() for rule in self.optimization_rules])
        optimized_node = optimizer.optimize(node)

        return self._render(optimized_node)

    @abstractmethod
    def _render(self, node: Node) -> T:
        """
        Defines an abstract method for rendering a node object into a string format.

        Summary:
        This method is intended to be overridden by subclasses to implement the rendering
        logic specific to the type of node being processed. It serves as a blueprint for
        rendering different node representations into their respective string outputs.

        Args:
            node (Node): The node object that needs to be rendered.

        Returns:
            str: A string representation of the provided node.
        """
