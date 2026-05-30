from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec("null_handling", "is_null")
def test_is(f: TBaseField, expected_result: TExpectedResult) -> None:
    assert f("status").is_null().compile() == expected_result


@mark.spec("null_handling", "is_not_null")
def test_is_not(f: TBaseField, expected_result: TExpectedResult) -> None:
    assert f("status").is_not_null().compile() == expected_result
