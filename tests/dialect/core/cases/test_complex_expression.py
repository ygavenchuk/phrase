from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec("complex_expression", 1)
def test_1(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ((f("foo") > 123) & f("bar").in_([1, 2])) | ~(f("baz") == None)  # noqa: E711
    assert expression.compile() == expected_result


@mark.spec("complex_expression", 2)
def test_2(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (
        ((f("foo") > 123) & f("bar").in_([1, 2]))
        | ~((f("baz") == None) | (f("blah") == "lorem ipsum"))  # noqa: E711
    )
    assert expression.compile() == expected_result
