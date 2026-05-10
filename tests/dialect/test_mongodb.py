from datetime import UTC, datetime
from decimal import Decimal

import pytest

from pyphrase.base.ast.node import ConstantNode, Node, UnaryNode
from pyphrase.base.operator import UnaryOperator
from pyphrase.dialect.mongodb import C, F, MongoCompiler


def test_mongo_basic_operators() -> None:
    """
    Test standard binary operators mapping to Mongo prefix keys.
    """
    # Inequality
    assert (F("age") != 25).compile() == {"age": {"$ne": 25}}

    # Greater/Less than
    assert (F("price") > 100).compile() == {"price": {"$gt": 100}}
    assert (F("price") >= 100).compile() == {"price": {"$gte": 100}}
    assert (F("stock") < 5).compile() == {"stock": {"$lt": 5}}

    # IN operator
    assert F("role").in_(["admin", "staff"]).compile() == {
        "role": {"$in": ["admin", "staff"]}
    }


def test_mongo_string_pattern_matching() -> None:
    """
    Test that LIKE is correctly translated to $regex.
    """
    # Simple LIKE
    expr = F("email").like(r"@gmail\.com$")
    assert expr.compile() == {"email": {"$regex": r"@gmail\.com$"}}


def test_mongo_unary_operators() -> None:
    """
    Test NULL checks mapping to $exists or equality with None.
    In Mongo, "is null" often maps to {field: None}.
    """
    # IS NULL
    assert (F("deleted_at") == None).compile() == {"deleted_at": None}  # noqa: E711

    # IS NOT NULL (often rendered as $ne: None)
    # Note: Depending on your NullOptimizationRule, this might change
    node = F("updated_at") != None  # noqa: E711
    assert node.compile() == {"updated_at": {"$ne": None}}


def test_mongo_inversion_not() -> None:
    """
    Test the NOT operator (UnaryNode).
    In MongoDB, $not is an operator that wraps a constraint.
    """
    # NOT (age > 18) -> { age: { $lte: 18 } } }
    expr = ~(F("age") > 18)
    assert expr.compile() == {"age": {"$lte": 18}}


def test_mongo_not_like_inversion() -> None:
    """
    Test that NOT LIKE becomes a $not $regex combination.
    """
    expr = F("name").not_like("Admin%")
    assert expr.compile() == {"name": {"$not": {"$regex": "Admin%"}}}
    expr = ~(F("name").like("Admin%"))
    assert expr.compile() == {"name": {"$not": {"$regex": "Admin%"}}}


def test_mongo_complex_logical_nesting() -> None:
    """
    Test nested AND/OR with inversions.
    """
    # (status == 'active' OR (age >= 18 AND score != 0))
    # Note: Your MongoCompiler needs to handle BinaryOperator.OR
    expr = (F("status") == "active") | ((F("age") >= 18) & (F("score") != 0))

    expected = {
        "$or": [
            {"status": "active"},
            {"$and": [{"age": {"$gte": 18}}, {"score": {"$ne": 0}}]},
        ]
    }
    assert expr.compile() == expected


def test_mongo_expression_with_f_and_c() -> None:
    """
    Test that MongoCompiler correctly unpacks value from ConstantNode
    using pattern matching and handles raw values.
    """
    # `F("score") == 100`  creates inside BinaryConstraint(..., ConstantNode(100))
    expr1 = F("score") == 100
    assert expr1.compile() == {"score": 100}

    # 2. explicit using `C` for constant values
    expr2 = F("status") == C("active")
    assert expr2.compile() == {"status": "active"}

    # Checking operators with `F` and `C`
    expr3 = F("age") > C(18)
    assert expr3.compile() == {"age": {"$gt": 18}}

    expr4 = F("deleted_at") == C.null()
    assert expr4.compile() == {"deleted_at": None}


def test_mongo_not_empty_node() -> None:
    class EmptyNode(Node):
        pass

    expr = UnaryNode(EmptyNode(), UnaryOperator.NOT)
    compiler = MongoCompiler()

    with pytest.raises(NotImplementedError):
        compiler._render(expr)  # noqa: SLF001


def test_render_null_literal() -> None:
    """
    Test that `SQLiteRenderer` correctly renders NULL literals.
    """
    expr = C.null()

    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is None

    assert expr.compile() is None


def test_not_constant_node() -> None:
    assert not (~C("foo")).compile()
    assert not (~C(123)).compile()


@pytest.mark.parametrize(
    ["input_time", "expected"],
    [
        (datetime(2000, 1, 2, 3, 4, 5), {"created_at": datetime(2000, 1, 2, 3, 4, 5)}),
        (
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC),
            {"created_at": datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC)},
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 678000),
            {"created_at": datetime(2000, 1, 2, 3, 4, 5, 678000)},
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC),
            {"created_at": datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC)},
        ),
    ],
)
def test_handling_datetime(input_time: datetime, expected: dict[str, datetime]) -> None:
    expr = F("created_at") == input_time
    assert expr.compile() == expected


@pytest.mark.parametrize(
    ["cost", "expected"],
    [
        (Decimal("124.45"), {"cost": Decimal("124.45")}),
        (Decimal(0), {"cost": Decimal(0)}),
        (Decimal("0.00"), {"cost": Decimal("0.00")}),
        (Decimal("1.12345"), {"cost": Decimal("1.12345")}),
        (Decimal("12345.67"), {"cost": Decimal("12345.67")}),
        (Decimal(1234), {"cost": Decimal(1234)}),
        (Decimal(-12345), {"cost": Decimal(-12345)}),
        (Decimal("-1234.6789"), {"cost": Decimal("-1234.6789")}),
    ],
)
def test_handling_decimal(cost: Decimal, expected: dict[str, Decimal]) -> None:
    expr = F("cost") == cost
    assert expr.compile() == expected
