from enum import StrEnum

__all__ = (
    "BinaryOperator",
    "LikeOperator",
    "LogicalOperator",
    "Operator",
    "UnaryOperator",
)


class Operator(StrEnum):
    pass


class BinaryOperator(Operator):
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IN = "IN"
    NOT_IN = "NOT IN"


class LogicalOperator(Operator):
    AND = "AND"
    OR = "OR"


class UnaryOperator(Operator):
    NOT = "NOT"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


class LikeOperator(Operator):
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    ILIKE = "ILIKE"
    NOT_ILIKE = "NOT ILIKE"
