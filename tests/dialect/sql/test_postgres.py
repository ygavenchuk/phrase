from pyphrase.dialect.sql.postgres import C, F


def test_pg_ilike_operator_rendering() -> None:
    """
    Test that the Postgres-specific `ILIKE` operator renders correctly.
    """
    assert str(F("username").ilike("admin%")) == "\"username\" ILIKE 'admin%'"
    assert str(F("username").not_ilike("admin%")) == "\"username\" NOT ILIKE 'admin%'"


def test_pg_not_ilike_inversion() -> None:
    """
    Test that `NOT (field ILIKE pattern)` is optimized to `NOT ILIKE`.
    """
    expr = ~(F("email").ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" NOT ILIKE '%@GMAIL.COM'"

    expr = ~(F("email").not_ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" ILIKE '%@GMAIL.COM'"


def test_pg_complex_ilike_and_null() -> None:
    """
    Test combination of ILIKE and NULL checks for Postgres.
    """
    expr = (F("tags").ilike("%python%")) & (F("deleted_at") == C.null())

    expected = '("tags" ILIKE \'%python%\') AND ("deleted_at" IS NULL)'
    assert str(expr) == expected
