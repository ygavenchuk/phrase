import pytest

from pyphrase.base.ast.node import Node, UnaryNode
from pyphrase.base.operator import UnaryOperator
from pyphrase.dialect.mongodb import MongoCompiler


def test_mongo_not_empty_node() -> None:
    class EmptyNode(Node):
        pass

    expr = UnaryNode(EmptyNode(), UnaryOperator.NOT)
    compiler = MongoCompiler()

    with pytest.raises(NotImplementedError):
        compiler._render(expr)  # noqa: SLF001
