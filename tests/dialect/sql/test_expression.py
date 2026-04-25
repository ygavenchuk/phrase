import pytest

from phrase.dialect.sql.common import C, F


# basic comparisons (Atomic Predicates)
def test_field_comparison_to_string() -> None:
    assert str(F("age") == 25) == '"age" = 25'
    assert str(F("age") != 25) == '"age" != 25'
    assert str(F("field") == "admin") == "\"field\" = 'admin'"
    assert str(F("score") > 100) == '"score" > 100'
    assert str(F("score") >= 100) == '"score" >= 100'
    assert str(F("score") < 100) == '"score" < 100'
    assert str(F("score") <= 100) == '"score" <= 100'


def test_field_null_handling() -> None:
    assert str(F("deleted_at") == None) == '"deleted_at" IS NULL'  # noqa: E711
    assert str(F("deleted_at").is_null()) == '"deleted_at" IS NULL'
    assert str(F("deleted_at").is_not_null()) == '"deleted_at" IS NOT NULL'
    assert str(~(F("status") == None)) == '"status" IS NOT NULL'  # noqa: E711
    assert str(F("status") != None) == '"status" IS NOT NULL'  # noqa: E711


def test_field_in_operator() -> None:
    bar_in = F("id").in_([1, 2, 3])

    assert str(bar_in) == '"id" IN (1, 2, 3)'
    assert str(~bar_in) == '"id" NOT IN (1, 2, 3)'
    assert str(~~bar_in) == '"id" IN (1, 2, 3)'


def test_field_not_in_operator() -> None:
    bar_not_in = F("id").not_in([1, 2, 3])

    assert str(bar_not_in) == '"id" NOT IN (1, 2, 3)'
    assert str(~bar_not_in) == '"id" IN (1, 2, 3)'
    assert str(~~bar_not_in) == '"id" NOT IN (1, 2, 3)'


def test_logical_junctions() -> None:
    f1 = F("a") == 1
    f2 = F("b") > 2

    # Simple AND
    assert str(f1 & f2) == '("a" = 1) AND ("b" > 2)'

    # Simple OR
    assert str(f1 | f2) == '("a" = 1) OR ("b" > 2)'


def test_not_null_operator() -> None:
    assert str(~F("a").is_null()) == '"a" IS NOT NULL'
    assert str(F("a").is_not_null()) == '"a" IS NOT NULL'
    assert str(F("a") != None) == '"a" IS NOT NULL'  # noqa: E711


def test_complex_expression_tree() -> None:
    foo = F("foo") > 123
    bar = F("bar").in_([1, 2])
    baz = F("baz") == None  # noqa: E711
    blah = F("blah") == "lorem ipsum"

    query1 = (foo & bar) | ~baz
    query2 = (foo & bar) | ~(baz | blah)

    expected1 = '(("foo" > 123) AND ("bar" IN (1, 2))) OR ("baz" IS NOT NULL)'
    expected2 = (
        '(("foo" > 123) AND ("bar" IN (1, 2))) OR '
        '(("baz" IS NOT NULL) AND ("blah" != \'lorem ipsum\'))'
    )

    assert str(query1) == expected1
    assert str(query2) == expected2


def test_operator_precedence() -> None:
    a = F("a") == 1
    b = F("b") == 2
    c = F("c") == 3

    query = a | b & c
    assert str(query) == '("a" = 1) OR (("b" = 2) AND ("c" = 3))'


def test_non_expression_operands() -> None:
    # Checks that we cannot apply a logical operator to a non-expression thing
    with pytest.raises(TypeError):
        # attempt to use "AND" between expression and a regular number
        _ = (F("a") == 1) & 123

    with pytest.raises(TypeError):
        # attempt to use "AND" between expression and a regular number
        _ = (F("a") == 1) | 123


def test_between_operator() -> None:
    assert str(F("age").between(18, 30)) == '("age" >= 18) AND ("age" <= 30)'


def test_optimization_de_morgan_and() -> None:
    # NOT (a AND b) -> NOT a OR NOT b
    expr = ~((F("age") > 18) & (F("status") == "active"))
    assert str(expr) == '("age" <= 18) OR ("status" != \'active\')'


def test_optimization_de_morgan_or() -> None:
    # NOT (a OR b) -> NOT a AND NOT b
    expr = ~((F("score") < 0) | (F("score") > 100))
    assert str(expr) == '("score" >= 0) AND ("score" <= 100)'


def test_constant_folding_not() -> None:
    # NOT TRUE -> FALSE / NOT FALSE -> TRUE
    assert str(~C(True)) == "FALSE"
    assert str(~C(False)) == "TRUE"


def test_constant_folding_and_true() -> None:
    # X AND TRUE -> X
    expr = (F("age") > 18) & True
    assert str(expr) == '"age" > 18'

    # TRUE AND X -> X
    expr = C(True) & (F("status") == "active")
    assert str(expr) == "\"status\" = 'active'"


def test_constant_folding_and_false() -> None:
    # X AND FALSE -> FALSE
    expr = (F("age") > 18) & False
    assert str(expr) == "FALSE"

    # FALSE AND X -> FALSE
    expr = F.constant(False) & (F("status") == "active")
    assert str(expr) == "FALSE"


def test_constant_folding_or_true() -> None:
    # X OR TRUE -> TRUE
    expr = (F("age") > 18) | True
    assert str(expr) == "TRUE"


def test_constant_folding_or_false() -> None:
    # X OR FALSE -> X
    expr = (F("age") > 18) | False
    assert str(expr) == '"age" > 18'


def test_constant_folding_complex_nested() -> None:
    # (A AND TRUE) OR (B AND FALSE) -> A OR FALSE -> A
    expr = ((F("a") == 1) & True) | ((F("b") == 2) & False)
    assert str(expr) == '"a" = 1'


def test_constant_folding_with_de_morgan() -> None:
    # NOT (A AND FALSE) -> NOT (FALSE) -> TRUE
    expr = ~((F("a") > 10) & False)
    assert str(expr) == "TRUE"


def test_constant_folding_or_true_left() -> None:
    # TRUE OR (field == 'value') -> TRUE
    expr = True | (F("status") == "active")
    assert str(expr) == "TRUE"


def test_constant_folding_and_true_left() -> None:
    # TRUE OR (field == 'value') -> TRUE
    expr = True & (F("status") == "active")
    assert str(expr) == "\"status\" = 'active'"


def test_constant_folding_or_false_left() -> None:
    # TRUE OR (field == 'value') -> TRUE
    expr = False | (F("status") == "active")
    assert str(expr) == "\"status\" = 'active'"


def test_constant_folding_or_true_right() -> None:
    # (field == 'value') OR TRUE -> TRUE
    expr = (F("status") == "active") | True
    assert str(expr) == "TRUE"


def test_constant_folding_or_both_true() -> None:
    # TRUE OR TRUE -> TRUE
    expr = C.true() | True
    assert str(expr) == "TRUE"
