from collections.abc import Mapping

from pyphrase.base.factory import BaseField, ConstantFactory
from pyphrase.dialect.mongodb import TMongoRendered

type TBaseField = type[BaseField[str | TMongoRendered]]
type TConstant = ConstantFactory[str | TMongoRendered]
type TExpectedResult = str | TMongoRendered
type TFixtureData = TExpectedResult | Mapping[str, TFixtureData]
