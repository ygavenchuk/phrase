from pyphrase.dialect.sql.mssql import C, F


def test_mssql_brackets_and_bit() -> None:
    expr = F("dbo.users.is_active") == C.true()
    assert str(expr) == "[dbo].[users].[is_active] = 1"


def test_mssql_reserved_word() -> None:
    expr = F("order") == "desc"
    assert str(expr) == "[order] = 'desc'"
