"""
This module contains utilities for optimizing Abstract Syntax Trees (AST)
through iterative post-order traversal and transformation rule application.

The primary functionality is centered around the ASTOptimizer class, which
applies transformation rules to nodes in a bottom-up manner to optimize the AST.
It is designed to handle complex and deeply nested trees without running into
recursion limitations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyphrase.base.ast.node import BinaryNode, Node, UnaryNode

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyphrase.base.ast.rules import TransformationRule


@dataclass(slots=True)
class TraversalFrame:
    """Represents a single frame in the iterative AST traversal."""

    node: Node
    children_visited: bool = False


class ASTOptimizer:
    """
    Optimizes an Abstract Syntax Tree (AST) by applying transformation rules
    in a bottom-up, non-recursive manner.
    """

    __slots__ = ("_rules",)

    def __init__(self, rules: Iterable[TransformationRule]) -> None:
        """
        Initializes the optimizer with a set of transformation rules.

        :param rules: A sequence of rules to be applied to each node.
        """
        self._rules = rules

    def optimize(self, root: Node) -> Node:
        """
        Performs AST optimization using an iterative post-order traversal (bottom-up)

        This avoids RecursionError for deep ASTs and handles frozen dataclasses.

        :param root: The root node of the AST to optimize.

        Returns:
            The fully optimized AST root.
        """
        # Initialize stack with the root frame
        stack: list[TraversalFrame] = [TraversalFrame(node=root)]

        # Maps original node IDs to their newly created optimized counterparts
        optimized_cache: dict[int, Node] = {}

        # Explicit type hint for current_optimized to prevent mypy assignment errors
        current_optimized: Node

        while stack:
            frame = stack[-1]
            curr_node = frame.node

            if not frame.children_visited:
                frame.children_visited = True

                # Phase 1: Push children to stack
                match curr_node:
                    case BinaryNode(left, _, right):
                        stack.append(TraversalFrame(node=right))
                        stack.append(TraversalFrame(node=left))
                    case UnaryNode(child, _):
                        stack.append(TraversalFrame(node=child))
                    case _:
                        # Leaf nodes have no children to push
                        pass
            else:
                stack.pop()

                # Phase 2: Reconstruct node and apply rules
                match curr_node:
                    case BinaryNode(left, operator, right):
                        current_optimized = BinaryNode(
                            left=optimized_cache.pop(id(left)),
                            operator=operator,
                            right=optimized_cache.pop(id(right)),
                        )
                    case UnaryNode(child, operator):
                        current_optimized = UnaryNode(
                            node=optimized_cache.pop(id(child)), operator=operator
                        )
                    case _:
                        current_optimized = curr_node

                # Apply transformation rules
                for rule in self._rules:
                    current_optimized = rule.apply(current_optimized)

                optimized_cache[id(curr_node)] = current_optimized

        return optimized_cache[id(root)]
