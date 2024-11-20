from copy import deepcopy
from typing import Any, List, cast

import pytest
from pydantic import ValidationError

from gib_esu.models.service_models import Durum, Sonuc, Yanit


@pytest.fixture(scope="module")
def my_model() -> dict:
    return {
        "durum": Durum.SUCCESS,
        "sonuc": [
            {"esu_seri_no": "AB535", "sira_no": 1, "kod": "1000", "mesaj": "Basarili"}
        ],
    }


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
        (["durum"], "invalid"),
        (["durum"], ""),
        (["sonuc", 0, "esu_seri_no"], "AB"),
        (["sonuc", 0, "esu_seri_no"], ""),
        (["sonuc", 0, "sira_no"], "A1"),
        (["sonuc", 0, "sira_no"], 0),
        (["sonuc", 0, "sira_no"], ""),
        (["sonuc", 0, "kod"], "10"),
        (["sonuc", 0, "kod"], ""),
    ],
)
def test_api_yanit_model(my_model: Yanit, keys: List[str], invalid_value: Any) -> None:
    """Test api_yanit.Yanit validation faiures."""

    test_model = cast(dict, deepcopy(my_model))

    set_nested_field(test_model, keys, invalid_value)

    with pytest.raises(ValidationError) as e:
        Yanit(
            durum=test_model["durum"],
            sonuc=[
                Sonuc(
                    esu_seri_no=test_model["sonuc"][0]["esu_seri_no"],
                    sira_no=test_model["sonuc"][0]["esu_seri_no"],
                    kod=test_model["sonuc"][0]["kod"],
                    mesaj=test_model["sonuc"][0]["mesaj"],
                )
            ],
        )
    assert e.value.errors()[0].get("msg") is not None
