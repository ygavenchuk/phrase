from pyphrase.dialect.sql.qgis import F


def test_qgis_ilike_operator_rendering() -> None:
    """
    Test that the Postgres-specific `ILIKE` operator renders correctly.
    """
    assert str(F("username").ilike("admin%")) == "\"username\" ILIKE 'admin%'"
    assert str(F("username").not_ilike("admin%")) == "\"username\" NOT ILIKE 'admin%'"


def test_qgis_not_ilike_inversion() -> None:
    """
    Test that `NOT (field ILIKE pattern)` is optimized to `NOT ILIKE`.
    """
    expr = ~(F("email").ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" NOT ILIKE '%@GMAIL.COM'"

    expr = ~(F("email").not_ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" ILIKE '%@GMAIL.COM'"
