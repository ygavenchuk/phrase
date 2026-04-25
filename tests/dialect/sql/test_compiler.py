import pytest

from phrase.base.ast.node import ConstantNode, Node, UnaryNode
from phrase.base.operator import UnaryOperator
from phrase.dialect.sql.common import SQLCompiler


def test_render_generic_unary_node_fallback() -> None:
    """
    Test the basic rendering of a UnaryNode for cases that
    do not match specialized patterns (like NOT IN).
    """
    # Manually create a node to bypass F-class logic
    # that might trigger advanced optimization rules.
    # Expected structure: NOT (TRUE)
    node = UnaryNode(node=ConstantNode(value=True), operator=UnaryOperator.NOT)

    compiler = SQLCompiler()

    # Call _render directly. Since ConstantNode is not a BinaryConstraint,
    # the compiler should fall through to the generic UnaryNode case.
    result = compiler._render(node)  # noqa: SLF001

    assert result == "NOT (TRUE)"


def test_render_unknown_node_raises_error() -> None:
    class FutureNode(Node):
        pass

    compiler = SQLCompiler()
    with pytest.raises(
        NotImplementedError, match="No render rule for node type: FutureNode"
    ):
        compiler._render(FutureNode())  # noqa: SLF001
