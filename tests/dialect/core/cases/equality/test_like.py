from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec("equality", "like")
def test_like(f: TBaseField, expected_result: TExpectedResult) -> None:
    expr = f("product_name").like("Banana%")  # type: ignore[attr-defined]

    # Check both the operator and the quoting
    assert expr.compile() == expected_result


@mark.spec("equality", "not_like")
def test_not_like(f: TBaseField, expected_result: TExpectedResult) -> None:
    expr = f("sku").not_like("OLD-%")  # type: ignore[attr-defined]

    # Check both the operator and the quoting
    assert expr.compile() == expected_result
