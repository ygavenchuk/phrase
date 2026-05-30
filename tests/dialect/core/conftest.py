from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import Mark, Metafunc

from tests.dialect.core.infrastructure.fixtures import (
    DIALECTS,
    constant_factory,
    expected_result,
    field_factory,
)

if TYPE_CHECKING:
    from pyphrase.base.types import LiteralValue


# list fixtures to let `ruff` know they are used for pytest
__all__ = [
    "constant_factory",
    "expected_result",
    "field_factory",
]


def _parse_spec_marker(variants: dict[str, LiteralValue]) -> list[str]:
    """
    Parses the specification markers based on the structure of the given variants.

    Determines the keys for markers based on the type of the first value in the
    `variants` dictionary. The keys represent the expected structure for different
    types of values.

    Parameters:
        variants (dict[str, LiteralValue]): A dictionary where keys are strings and
        values are of type LiteralValue. The type of the first value in this dictionary
        will determine the returned list of keys.

    Returns:
        list[str]: A list of marker keys appropriate for the type of the first value
        in the given dictionary.
    """
    first_value = next(iter(variants.values()))

    match first_value:
        case tuple() | list():
            return ["dialect", "value_type", "field_name", "value"]
        case _:
            return ["dialect", "value_type", "value"]


def _generate_variant_tests(
    metafunc: Metafunc, base_keys: tuple[str], variants: dict[str, LiteralValue]
) -> None:
    """
    Generates and applies parameterized test cases for use in pytest

    This function creates test case combinations by iterating through provided test
    variants and applies them to pytest metafunc objects. Custom identifiers are
    created for each test case based on dialects, base keys, and variant keys.
    Resulting parameterization is added to the metafunc for execution in pytest.

    Parameters:
        metafunc: Metafunc
            The pytest metafunc object, which is used during test generation to
            define combinations of inputs for parameterized tests.
        base_keys: tuple[str]
            A tuple representing base keys, used for generating default test identifiers.
        variants: dict[str, LiteralValue]
            A dictionary of input variants where keys represent variant names and
            values represent a list, tuple, or single value for specific inputs.
    """
    argument_names = _parse_spec_marker(variants)

    for name in argument_names:
        if name not in metafunc.fixturenames:
            metafunc.fixturenames.append(name)

    argument_values = []
    custom_ids = []

    base_case_id = "-".join(str(k) for k in base_keys)
    for dialect in DIALECTS:
        for var_key, var_values in variants.items():
            match var_values:
                case tuple(args) | list(args):
                    argument_values.append((dialect, var_key, *args))
                case _:
                    argument_values.append((dialect, var_key, var_values))

            custom_ids.append(f"{dialect}-{base_case_id}-{var_key}")

    metafunc.parametrize(
        argument_names, argument_values, scope="function", ids=custom_ids
    )


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """
    Generates exactly one test per dialect, reading keys from the "official" marker
    """
    if not {"f", "c", "expected_result"} & set(metafunc.fixturenames):
        return

    if "dialect" not in metafunc.fixturenames:
        metafunc.fixturenames.append("dialect")

    # Looking for the `spec` parker among other own markers
    spec = next((m for m in metafunc.definition.own_markers if m.name == "spec"), None)

    # unpack Mark object
    match spec:
        case Mark(args=tuple(base_keys), kwargs={"variant": dict(variants)}) if variants:
            _generate_variant_tests(metafunc, base_keys, variants)
        case Mark(args=tuple(keys)) if keys:
            case_id = "-".join(str(k) for k in keys)
            custom_ids = [f"{dialect}-{case_id}" for dialect in DIALECTS]
            metafunc.parametrize("dialect", DIALECTS, scope="function", ids=custom_ids)
        case _:
            metafunc.parametrize("dialect", DIALECTS, scope="function")
