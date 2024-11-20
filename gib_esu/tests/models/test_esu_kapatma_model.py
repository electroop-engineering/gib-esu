from copy import deepcopy
from typing import List, cast

import pytest
from pydantic import ValidationError

from gib_esu.models.api_models import ESUKapatmaModel, ESUSeriNo


@pytest.fixture(scope="module")
def my_model() -> ESUKapatmaModel:
    return ESUKapatmaModel(
        firma_kodu="J000",
        kapatma_bilgisi=ESUSeriNo(
            esu_seri_no="123",
        ),
    )


# Helper function to modify nested fields
def set_nested_field(data: dict, keys: list, value: str) -> None:
    d = data
    for key in keys[:-1]:
        if isinstance(key, int) and isinstance(d, list):
            while len(d) <= key:
                d.append({})
            d = d[key]
        else:
            d = d.setdefault(key, {})
    d[keys[-1]] = value


@pytest.mark.parametrize(
    "keys, invalid_value",
    [
        (["firma_kodu"], ""),
        (["kapatma_bilgisi", "esu_seri_no"], ""),
    ],
)
def test_esu_kapatma_model_validation_failure_cases(
    my_model: ESUKapatmaModel,
    keys: List[str],
    invalid_value: str,
) -> None:
    """Test ESUKapatmaModel validation faiures."""

    test_model = cast(dict, deepcopy(my_model.model_dump()))

    set_nested_field(test_model, keys, invalid_value)

    with pytest.raises(ValidationError) as e:
        ESUKapatmaModel(**test_model)
    assert e.value.errors()[0].get("msg") is not None


def test_esu_kapatma_model_validation_success_case(my_model: ESUKapatmaModel) -> None:
    """Test ESUKapatmaModel successful construction."""
    try:
        ESUKapatmaModel(**my_model.model_dump())
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
