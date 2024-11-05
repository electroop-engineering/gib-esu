from copy import deepcopy
from typing import List, cast

import pytest
from pydantic import ValidationError

from models.esu_mukellef import (FATURA_ERROR, FATURA_ETTN_ERROR,
                                 FATURA_TARIHI_ERROR, FIRMA_KODU_ERROR,
                                 IL_KODU_ERROR, ILCE_ERROR,
                                 MUKELLEF_UNVAN_ERROR, MUKELLEF_VKN_ERROR,
                                 MULKIYET_SAHIBI_AD_UNVAN_ERROR,
                                 MULKIYET_SAHIBI_VKN_TCKN_ERROR,
                                 MULKİYET_ERROR, SERI_NO_ERROR,
                                 SERTIFIKA_ERROR, SERTIFIKA_TARIHI_ERROR,
                                 SERTIFIKA_VE_MULKIYET_ERROR,
                                 YA_FATURA_YA_MULKIYET_ERROR, ESUMukellef,
                                 ESUMukellefBilgisi, ESUMukellefModel)


@pytest.fixture(scope="module")
def my_model() -> ESUMukellefModel:
    return ESUMukellefModel(
        firma_kodu="J000",
        durum_bilgileri=ESUMukellefBilgisi(
            esu_seri_no="123",
            il_kodu="034",
            ilce="Beşiktaş",
            adres_numarası="",
            koordinat="",
            mukellef_vkn="0123456789",
            mukellef_unvan="Test Mukellef",
            sertifika_no="",
            sertifika_tarihi="",
            fatura_tarihi="19.12.2024",
            fatura_ettn="P01C5368",
            mulkiyet_sahibi_vkn_tckn="",
            mulkiyet_sahibi_ad_unvan="",
        ),
    )


# Helper function to modify nested fields
def set_nested_field(data: dict, keys: List[str], value: str) -> None:
    d = data
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


@pytest.mark.parametrize(
    "keys, invalid_value, expected_error",
    [
        ("durum_bilgileri>fatura_ettn", "", FATURA_ERROR),
        ("durum_bilgileri>mulkiyet_sahibi_ad_unvan", "ABC A.Ş.", MULKİYET_ERROR),
        ("durum_bilgileri>sertifika_tarihi", "2024-12-30", SERTIFIKA_ERROR),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan"
            ),
            "1234567890*ABC A.Ş.",
            YA_FATURA_YA_MULKIYET_ERROR,
        ),
        (
            "durum_bilgileri>fatura_ettn*durum_bilgileri>fatura_tarihi",
            "*",
            YA_FATURA_YA_MULKIYET_ERROR,
        ),
        (
            "durum_bilgileri>sertifika_no*durum_bilgileri>sertifika_tarihi",
            "CERT01*2024-12-30",
            SERTIFIKA_VE_MULKIYET_ERROR,
        ),
        ("firma_kodu", "J0", FIRMA_KODU_ERROR),
        ("durum_bilgileri>esu_seri_no", "A", SERI_NO_ERROR),
        ("durum_bilgileri>il_kodu", "34", IL_KODU_ERROR),
        ("durum_bilgileri>ilce", "Ç", ILCE_ERROR),
        ("durum_bilgileri>mukellef_vkn", "1234", MUKELLEF_VKN_ERROR),
        ("durum_bilgileri>mukellef_unvan", "F", MUKELLEF_UNVAN_ERROR),
        ("durum_bilgileri>fatura_tarihi", "23-05-2024", FATURA_TARIHI_ERROR),
        ("durum_bilgileri>fatura_ettn", "XX", FATURA_ETTN_ERROR),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*durum_bilgileri>fatura_tarihi"
            ),
            "012345678901*ABC A.Ş.**",
            MULKIYET_SAHIBI_VKN_TCKN_ERROR,
        ),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*durum_bilgileri>fatura_tarihi"
            ),
            "0123456789*X**",
            MULKIYET_SAHIBI_AD_UNVAN_ERROR,
        ),
        (
            (
                "durum_bilgileri>sertifika_tarihi*durum_bilgileri>sertifika_no*"
                "durum_bilgileri>fatura_ettn*durum_bilgileri>fatura_tarihi*"
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan"
            ),
            "23-05-2004*CERT01***0123456789*ABC A.Ş.",
            SERTIFIKA_TARIHI_ERROR,
        ),
    ],
)
def test_esu_mukellef_model_validation_failure_cases(
    my_model: ESUMukellefModel,
    keys: str,
    invalid_value: str,
    expected_error: str,
) -> None:
    """Test ESUMukellefModel construction and validation failures."""

    test_model = cast(dict, deepcopy(my_model))

    keys_arr = keys.split("*")
    values_arr = invalid_value.split("*")
    for index, item in enumerate(keys_arr):
        set_nested_field(test_model, item.split(">"), values_arr[index])

    with pytest.raises(ValidationError) as e:
        ESUMukellef(model=cast(ESUMukellefModel, test_model))
    assert str(e.value.errors()[0].get("msg")).split(", ")[1] == expected_error


def test_esu_mukellef_model_validation_success_case(my_model: ESUMukellefModel) -> None:
    """Test ESUMukellefModel construction and validation success."""
    try:
        ESUMukellef(model=my_model)
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
