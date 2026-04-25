from datetime import UTC, datetime
from decimal import Decimal

import pytest

from phrase.base.ast.node import ConstantNode
from phrase.dialect.sql.sqlite import C, F


def test_sqlite_field_rendering() -> None:
    """
    Ensure SQLiteF uses double quotes for field names.
    """
    expr = F("user_name") == "John"
    assert str(expr) == "\"user_name\" = 'John'"


@pytest.mark.parametrize(
    ["input_time", "expected"],
    [
        (datetime(2000, 1, 2, 3, 4, 5), "\"created_at\" = '2000-01-02 03:04:05'"),
        (
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC),
            "\"created_at\" = '2000-01-02 03:04:05+00:00'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 678000),
            "\"created_at\" = '2000-01-02 03:04:05.678'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC),
            "\"created_at\" = '2000-01-02 03:04:05.067+00:00'",
        ),
    ],
)
def test_handling_datetime(input_time: datetime, expected: str) -> None:
    expr = F("created_at") == input_time
    assert str(expr) == expected


@pytest.mark.parametrize(
    ["cost", "expected"],
    [
        ("124.45", '"cost" = 124.45'),
        ("0", '"cost" = 0'),
        ("0.00", '"cost" = 0.00'),
        ("1.12345", '"cost" = 1.12345'),
        ("12345.67", '"cost" = 12345.67'),
        ("1234", '"cost" = 1234'),
        ("-12345", '"cost" = -12345'),
        ("-1234.6789", '"cost" = -1234.6789'),
    ],
)
def test_handling_decimal(cost: str, expected: str) -> None:
    expr = F("cost") == Decimal(cost)
    assert str(expr) == expected


def test_sqlite_null_optimization() -> None:
    """
    Verify that NullOptimizationRule works with SQLite-specific classes.
    """
    expr = F("deleted_at") == C.null()

    # The optimization rule should still trigger,
    # and the renderer should apply double quotes.
    assert str(expr) == '"deleted_at" IS NULL'


def test_sqlite_like_operator_rendering() -> None:
    """
    Verify that the like() method on SQLiteF produces correct SQL syntax.
    """
    # SQLiteF now explicitly has the .like() method
    expr = F("product_name").like("Apple%")

    # Check both the operator and the quoting
    assert str(expr) == "\"product_name\" LIKE 'Apple%'"


def test_sqlite_not_like_operator_rendering() -> None:
    """
    Verify that the not_like() method on SQLiteF produces the correct SQL syntax.
    """
    expr = F("sku").not_like("OLD-%")

    assert str(expr) == "\"sku\" NOT LIKE 'OLD-%'"


def test_sqlite_like_negation_logic() -> None:
    """
    Test that the NOT operator correctly inverts `LIKE` into `NOT LIKE` for SQLite.
    """
    # ~(SQLiteF.like()) should be optimized to NOT LIKE
    expr = ~(F("email").like("%@internal.com"))

    assert str(expr) == "\"email\" NOT LIKE '%@internal.com'"


def test_sqlite_not_like_negation_logic() -> None:
    """
    Test that the NOT operator correctly inverts `NOT LIKE` into `LIKE` for SQLite.
    """
    # ~(SQLiteF.like()) should be optimized to LIKE
    expr = ~(F("email").not_like("%@internal.com"))

    assert str(expr) == "\"email\" LIKE '%@internal.com'"


def test_sqlite_custom_operator_precedence() -> None:
    """
    Ensure LIKE operators work correctly within complex expressions.
    """
    # (type == 'book') AND (title LIKE 'Python%')
    expr = (F("type") == "book") & F("title").like("Python%")

    expected = "(\"type\" = 'book') AND (\"title\" LIKE 'Python%')"
    assert str(expr) == expected


def test_sqlite_complex_expression() -> None:
    """
    Check complex logic with SQLite formatting.
    """
    expr = (F("age") >= 18) & (F("status") != C.null())

    expected = '("age" >= 18) AND ("status" IS NOT NULL)'
    assert str(expr) == expected


def test_sqlite_in_operator_rendering() -> None:
    """
    Verify that the IN operator renders correctly with SQLite double quotes.
    """
    # Assuming F has an .in_() method that produces
    # `BinaryConstraint(field, BinaryOperator.IN, value)`
    expr = F("id").in_([1, 2, 3])

    assert str(expr) == '"id" IN (1, 2, 3)'


def test_sqlite_not_in_optimization() -> None:
    """
    Test that NOT (field IN (values)) is optimized to "field NOT IN (values)".
    """
    expr = ~(F("status").in_(["deleted", "banned"]))

    # InversionRule should handle NOT + IN -> NOT IN
    assert str(expr) == "\"status\" NOT IN ('deleted', 'banned')"


def test_sqlite_boolean_true_rendering() -> None:
    """
    Verify that c_sqlite.true() renders correctly.
    In standard SQL/SQLite it is typically TRUE.
    """
    expr = C.true()
    assert str(expr) == "TRUE"


def test_sqlite_boolean_false_rendering() -> None:
    """
    Verify that c_sqlite.false() renders correctly.
    """
    expr = C.false()
    assert str(expr) == "FALSE"


def test_sqlite_null_is_null_rendering() -> None:
    """
    Verify the rendering of IS NULL for SQLite fields.
    """
    assert str(F("profile_image").is_null()) == '"profile_image" IS NULL'
    assert str(F("profile_image") == None) == '"profile_image" IS NULL'  # noqa: E711


def test_sqlite_complex_mixed_expression() -> None:
    """
    Test a mix of IN, NULL, and LIKE operators in a single SQLite expression.
    """
    expr = (
        F("category_id").in_([10, 20])
        & F("description").like("Promo%")
        & (F("expired_at") != None)  # noqa: E711
    )

    expected = (
        '(("category_id" IN (10, 20)) AND '
        "(\"description\" LIKE 'Promo%')) AND "
        '("expired_at" IS NOT NULL)'
    )
    assert str(expr) == expected


def test_render_null_literal() -> None:
    """
    Test that `SQLiteRenderer` correctly renders NULL literals.
    """
    expr = C.null()

    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is None

    assert str(expr) == "NULL"
