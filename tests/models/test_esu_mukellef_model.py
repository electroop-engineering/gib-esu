from copy import deepcopy
from typing import List, cast

import pytest
from pydantic import ValidationError

from models.esu_mukellef import (
    ESUGuncelleme,
    ESUMukellef,
    ESUMukellefBilgisi,
    ESUMukellefModel,
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
            esu_seri_no="123",
            il_kodu="034",
            ilce="Beşiktaş",
            adres_numarası="",
            koordinat="",
            mukellef_vkn="0123456789",
            mukellef_unvan="Test Mukellef",
            sertifika_no="",
            sertifika_tarihi="",
            fatura_tarihi="2024-12-19",
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
    "keys, invalid_value",
    [
        ("durum_bilgileri>fatura_ettn", ""),
        ("durum_bilgileri>mulkiyet_sahibi_ad_unvan", "ABC A.Ş."),
        ("durum_bilgileri>sertifika_tarihi", "2024-12-30"),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan"
            ),
            "1234567890*ABC A.Ş.",
        ),
        (
            "durum_bilgileri>fatura_ettn*" "durum_bilgileri>fatura_tarihi",
            "*",
        ),
        (
            "durum_bilgileri>sertifika_no*" "durum_bilgileri>sertifika_tarihi",
            "CERT01*2024-12-30",
        ),
        ("firma_kodu", "J0"),
        ("durum_bilgileri>esu_seri_no", "A"),
        ("durum_bilgileri>il_kodu", "34"),
        ("durum_bilgileri>ilce", "Ç"),
        ("durum_bilgileri>mukellef_vkn", "1234"),
        ("durum_bilgileri>mukellef_unvan", "F"),
        ("durum_bilgileri>fatura_tarihi", "23-05-2024"),
        ("durum_bilgileri>fatura_ettn", "XX"),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi"
            ),
            "012345678901*ABC A.Ş.**",
        ),
        (
            (
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi"
            ),
            "0123456789*X**",
        ),
        (
            (
                "durum_bilgileri>sertifika_tarihi*"
                "durum_bilgileri>sertifika_no*"
                "durum_bilgileri>fatura_ettn*"
                "durum_bilgileri>fatura_tarihi*"
                "durum_bilgileri>mulkiyet_sahibi_vkn_tckn*"
                "durum_bilgileri>mulkiyet_sahibi_ad_unvan"
            ),
            "23-05-2004*CERT01***0123456789*ABC A.Ş.",
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
        ESUMukellef(model=cast(ESUMukellefModel, test_model))
    assert e.value.errors()[0].get("msg") is not None


def test_esu_mukellef_model_validation_success_case(my_model: ESUMukellefModel) -> None:
    """Test successful ESUMukellefModel instantiation."""
    try:
        ESUMukellef(model=my_model)
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")


def test_esu_mukellef_olustur(my_model: ESUMukellefModel) -> None:
    """Test ESUMukellef.olustur() and ESUGuncelleme.olustur() class methods."""

    durum = my_model.durum_bilgileri

    lokasyon = Lokasyon(
        il_kodu=durum.il_kodu,
        ilce=durum.ilce,
        adres_numarası=durum.adres_numarası,
        koordinat=durum.koordinat,
    )

    fatura = Fatura(
        fatura_ettn=durum.fatura_ettn,
        fatura_tarihi=durum.fatura_tarihi,
    )

    mukellef = Mukellef(
        mukellef_vkn=durum.mukellef_vkn,
        mukellef_unvan=durum.mukellef_unvan,
    )

    mulkiyet_sahibi = MulkiyetSahibi(
        mulkiyet_sahibi_vkn_tckn=durum.mulkiyet_sahibi_vkn_tckn,
        mulkiyet_sahibi_ad_unvan=durum.mulkiyet_sahibi_ad_unvan,
    )

    sertifika = Sertifika(
        sertifika_no=durum.sertifika_no,
        sertifika_tarihi=durum.sertifika_tarihi,
    )

    try:
        ESUMukellef.olustur(
            esu_seri_no=durum.esu_seri_no,
            firma_kodu=my_model.firma_kodu,
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
            mulkiyet_sahibi=mulkiyet_sahibi,
            sertifika=sertifika,
        )
        ESUMukellef.olustur(
            esu_seri_no="SN001",
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
        )
        ESUGuncelleme.olustur(
            esu_seri_no="SN001",
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
            mulkiyet_sahibi=mulkiyet_sahibi,
            sertifika=sertifika,
        )
        ESUGuncelleme.olustur(
            esu_seri_no="SN001",
            firma_kodu="J000",
            fatura=fatura,
            lokasyon=lokasyon,
        )
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
