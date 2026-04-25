from phrase.base.ast.node import ConstantNode
from phrase.dialect.sql import C, F


def test_constant_true_factory() -> None:
    """
    Test that C.true() creates an Expression with a ConstantNode(True).
    """
    expr = C.true()

    # Check the underlying AST node
    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is True

    # Check string representation (Integration with compiler)
    assert str(expr) == "TRUE"


def test_inversion_constant_true() -> None:
    """
    Tests the consistent behavior of logical inversion operations on constant
    truth values.
    """
    assert str(~C.true()) == "FALSE"
    assert str(~C(True)) == "FALSE"
    assert str(~(~C.true())) == "TRUE"
    assert str(~C.false()) == "TRUE"
    assert str(~C(False)) == "TRUE"
    assert str(~(~C.false())) == "FALSE"


def test_constant_false_factory() -> None:
    """
    Test that C.false() creates an Expression with a ConstantNode(False).
    """
    expr = C.false()

    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is False
    assert str(expr) == "FALSE"


def test_constant_null_factory() -> None:
    """
    Test that C.null() creates an Expression with a ConstantNode(None).
    """
    expr = C.null()

    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is None

    assert str(expr) == "NULL"


def test_constant_call_syntax() -> None:
    """
    Test the __call__ syntax of the ConstantFactory (C(value)).
    """
    # Test with an integer constant
    expr_int = C(42)
    assert isinstance(expr_int.node, ConstantNode)
    assert expr_int.node.value == 42
    assert str(expr_int) == "42"

    # Test with a string constant
    expr_str = C("active")
    assert isinstance(expr_str.node, ConstantNode)
    assert expr_str.node.value == "active"
    # Ensure compiler adds quotes for strings
    assert str(expr_str) == "'active'"


def test_constant_integration_in_logic() -> None:
    """
    Verify that constants from C factory integrate correctly
    with Field expressions (F).
    """
    # Complex expression: (status == 'active') AND TRUE
    expr = (F("status") == "active") & C.true()

    # After constant folding optimization, it should just be the field check
    assert str(expr) == "\"status\" = 'active'"


def test_constant_null_comparison_logic() -> None:
    """
    Verify how C.null() behaves in comparisons.
    """
    # Note: In SQL, 'val = NULL' is usually not what you want (use IS NULL),
    # but here we test the raw constant node rendering.
    assert str(F("deleted_at") == C.null()) == '"deleted_at" IS NULL'
    assert str(F("deleted_at") != C.null()) == '"deleted_at" IS NOT NULL'
