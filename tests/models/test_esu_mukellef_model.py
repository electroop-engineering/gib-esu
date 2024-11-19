from copy import deepcopy
from typing import List, cast

import pytest
from pydantic import ValidationError

from models.api_models import (
    ESUGuncellemeModel,
    ESUMukellefBilgisi,
    ESUMukellefModel,
    ESUSeriNo,
    Fatura,
    Lokasyon,
    Mukellef,
    MulkiyetSahibi,
    Sertifika,
)


@pytest.fixture(scope="module")
def my_model() -> ESUMukellefModel:
    return ESUMukellefModel(
        firma_kodu="J000",
        durum_bilgileri=ESUMukellefBilgisi(
            il_kodu="034",
            ilce="Beşiktaş",
            adres_numarası="",
            koordinat="",
            mukellef_vkn="1234567890",
            mukellef_unvan="Test Mukellef",
            sertifika_no="",
            sertifika_tarihi="",
            fatura_tarihi="2024-12-19",
            fatura_ettn="P01C5368",
            mulkiyet_sahibi_vkn_tckn="",
            mulkiyet_sahibi_ad_unvan="",
            esu_seri_no="123",
        ),
    )


# Helper function to modify nested fields
def set_nested_field(data: dict, keys: List[str], value: str) -> None:
    d = data
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value


@pytest.mark.parametrize(
    "keys, invalid_value",
    [
        ("durum_bilgileri>fatura_ettn", ""),
        ("durum_bilgileri>mulkiyet_sahibi_ad_unvan", "ABC A.Ş."),
        ("durum_bilgileri>sertifika_tarihi", "2024-12-30"),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi"
            ),
            "0123456789*ABC A.Ş.*A*2024-12-31",
        ),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi"
            ),
            "***",
        ),
        ("durum_bilgileri>fatura_tarihi", "23-05-2024"),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi*"
                "durum_bilgileri>sertifika_no*"
                "durum_bilgileri>sertifika_tarihi"
            ),
            "1234567890*ABC A.Ş.***CERT01*12-15-2024",
        ),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi"
            ),
            "012345678*ABC A.Ş.**",
        ),
    ],
)
def test_esu_mukellef_model_validation_failure_cases(
    my_model: ESUMukellefModel,
    keys: str,
    invalid_value: str,
) -> None:
    """Test ESUMukellefModel construction and validation failures."""

    test_model = cast(dict, deepcopy(my_model.model_dump()))

    keys_arr = keys.split("*")
    values_arr = invalid_value.split("*")
    for index, item in enumerate(keys_arr):
        set_nested_field(test_model, item.split(">"), values_arr[index])

    with pytest.raises(ValidationError) as e:
        ESUMukellefModel(**test_model)
    assert e.value.errors()[0].get("msg") is not None


def test_esu_mukellef_model_validation_success_case(my_model: ESUMukellefModel) -> None:
    """Test successful ESUMukellefModel instantiation."""
    try:
        ESUMukellefModel(**my_model.model_dump())
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")


def test_esu_mukellef_olustur(my_model: ESUMukellefModel) -> None:
    """Test ESUMukellef.olustur() and ESUGuncelleme.olustur() class methods."""

    durum = my_model.durum_bilgileri

    lokasyon = Lokasyon(**durum.model_dump())

    fatura = Fatura(**durum.model_dump())

    mukellef = Mukellef(**durum.model_dump())

    mulkiyet_sahibi = MulkiyetSahibi(**durum.model_dump())

    sertifika = Sertifika(**durum.model_dump())

    try:
        ESUMukellefModel.olustur(
            esu_seri_no=durum.esu_seri_no,
            firma_kodu=my_model.firma_kodu,
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
            mulkiyet_sahibi=mulkiyet_sahibi,
            sertifika=sertifika,
        )
        ESUMukellefModel.olustur(
            esu_seri_no="SN001",
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
        )
        ESUGuncellemeModel.olustur(
            esu_seri_no=ESUSeriNo(esu_seri_no="SN001"),
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
            mulkiyet_sahibi=mulkiyet_sahibi,
            sertifika=sertifika,
        )
        ESUGuncellemeModel.olustur(
            esu_seri_no=ESUSeriNo(esu_seri_no="SN001"),
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
        )
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
