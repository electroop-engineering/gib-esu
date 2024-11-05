from copy import deepcopy
from typing import List, cast

import pytest
from pydantic import ValidationError

from models.esu_kayit import (
    EPDK_LISANS_ERROR,
    ESU_MARKA_ERROR,
    ESU_MODEL_ERROR,
    FIRMA_KODU_ERROR,
    FIRMA_VKN_ERROR,
    SERI_NO_ERROR,
    SOKET_DETAY_ACDC_ERROR,
    SOKET_DETAY_TIP_ERROR,
    SOKET_DETAY_UZUNLUK_ERROR,
    SOKET_NO_ERROR,
    SOKET_SAYISI_ERROR,
    SOKET_TIPI_ERROR,
    ESUKayit,
    ESUKayitBilgisi,
    ESUKayitModel,
    ESUSoket,
)


@pytest.fixture(scope="module")
def my_model() -> ESUKayitModel:
    return ESUKayitModel(
        firma_kodu="J000",
        firma_vkn="0123456789",
        epdk_lisans_no="ŞH/12345-1/12345",
        kayit_bilgisi=ESUKayitBilgisi(
            esu_seri_no="123",
            esu_markasi="ABB",
            esu_modeli="DC-Model",
            esu_soket_tipi="AC/DC",
            esu_soket_sayisi="2",
            esu_soket_detay=[
                ESUSoket(soket_no="Soket1", soket_tip="AC"),
                ESUSoket(soket_no="Soket2", soket_tip="DC"),
            ],
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
    "keys, invalid_value, expected_error",
    [
        (["firma_kodu"], "", FIRMA_KODU_ERROR),
        (["firma_vkn"], "0123", FIRMA_VKN_ERROR),
        (["epdk_lisans_no"], "ŞH/111-1/22222", EPDK_LISANS_ERROR),
        (["kayit_bilgisi", "esu_seri_no"], "AB", SERI_NO_ERROR),
        (["kayit_bilgisi", "esu_markasi"], "", ESU_MARKA_ERROR),
        (["kayit_bilgisi", "esu_modeli"], "", ESU_MODEL_ERROR),
        (["kayit_bilgisi", "esu_soket_sayisi"], "AC", SOKET_SAYISI_ERROR),
        (["kayit_bilgisi", "esu_soket_tipi"], "DC/AC", SOKET_TIPI_ERROR),
        (
            ["kayit_bilgisi", "esu_soket_detay", 0, "soket_no"],
            "SoketX",
            SOKET_NO_ERROR,
        ),
        (["kayit_bilgisi", "esu_soket_tipi"], "DC", SOKET_DETAY_TIP_ERROR),
        (["kayit_bilgisi", "esu_soket_tipi"], "AC", SOKET_DETAY_TIP_ERROR),
        (
            ["kayit_bilgisi", "esu_soket_detay", 0, "soket_tip"],
            "DC",
            SOKET_DETAY_ACDC_ERROR,
        ),
    ],
)
def test_esu_kayit_model_validation_failure_cases(
    my_model: ESUKayitModel,
    keys: List[str],
    invalid_value: str,
    expected_error: str,
) -> None:
    """Test ESUKayitModel construction and validation faiures."""

    test_model = cast(dict, deepcopy(my_model))

    set_nested_field(test_model, keys, invalid_value)

    with pytest.raises(ValidationError) as e:
        ESUKayit(model=cast(ESUKayitModel, test_model))
    if expected_error != SOKET_TIPI_ERROR:
        assert str(e.value.errors()[0].get("msg")).split(", ")[1] == expected_error
    else:
        assert str(e.value.errors()[0].get("msg")) == expected_error


def test_esu_kayit_model_validation_failure_case_soket_detay_length(
    my_model: ESUKayitModel,
) -> None:
    """Test ESUKayitModel SOKET_DETAY_UZUNLUK_ERROR validation error."""

    test_model = cast(dict, deepcopy(my_model))

    test_model["kayit_bilgisi"]["esu_soket_detay"].append(
        ESUSoket(soket_no="Soket3", soket_tip="AC")
    )

    with pytest.raises(ValidationError) as e:
        ESUKayit(model=cast(ESUKayitModel, test_model))

    assert (
        str(e.value.errors()[0].get("msg")).split(", ")[1] == SOKET_DETAY_UZUNLUK_ERROR
    )


def test_esu_kayit_model_validation_success_case(my_model: ESUKayitModel) -> None:
    """Test ESUKayitModel construction and validation success."""
    try:
        ESUKayit(model=my_model)
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
