from copy import deepcopy
from typing import List, cast

import pytest
from gib_esu.models import ESU, ESUKayitModel, ESUTipi, Firma, Soket, SoketTipi
from pydantic import ValidationError


@pytest.fixture(scope="module")
def my_model() -> ESUKayitModel:
    return ESUKayitModel(
        firma_kodu="J000",
        firma_vkn="0123456789",
        firma_unvan="ABC A.Ş.",
        epdk_lisans_no="ŞH/12345-1/12345",
        kayit_bilgisi=ESU(
            esu_seri_no="123",
            esu_markasi="ABB",
            esu_modeli="DC-Model",
            esu_soket_tipi=ESUTipi.AC_DC,
            esu_soket_sayisi="2",
            esu_soket_detay=[
                Soket(soket_no="Soket1", soket_tip=SoketTipi.AC),
                Soket(soket_no="Soket2", soket_tip=SoketTipi.DC),
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
    "keys, invalid_value",
    [
        (["firma_kodu"], ""),
        (["firma_vkn"], "0123"),
        (["epdk_lisans_no"], " "),
        (["kayit_bilgisi", "esu_seri_no"], ""),
        (["kayit_bilgisi", "esu_markasi"], ""),
        (["kayit_bilgisi", "esu_modeli"], ""),
        (["kayit_bilgisi", "esu_soket_sayisi"], "AC"),
        (["kayit_bilgisi", "esu_soket_tipi"], "DC/AC"),
        (
            ["kayit_bilgisi", "esu_soket_detay", 0, "soket_no"],
            "SoketX",
        ),
        (["kayit_bilgisi", "esu_soket_tipi"], "DC"),
        (["kayit_bilgisi", "esu_soket_tipi"], "AC"),
        (
            ["kayit_bilgisi", "esu_soket_detay", 0, "soket_tip"],
            "DC",
        ),
    ],
)
def test_esu_kayit_model_validation_failure_cases(
    my_model: ESUKayitModel,
    keys: List[str],
    invalid_value: str,
) -> None:
    """Test ESUKayitModel construction and validation faiures."""

    test_model = cast(dict, deepcopy(my_model.dict()))

    set_nested_field(test_model, keys, invalid_value)

    with pytest.raises(ValidationError) as e:
        ESUKayitModel(**test_model)
    assert e.value.errors()[0].get("msg") is not None


def test_esu_kayit_model_validation_failure_case_soket_detay_length(
    my_model: ESUKayitModel,
) -> None:
    """Test ESUKayitModel SOKET_DETAY_UZUNLUK_ERROR validation error."""

    test_model = cast(dict, deepcopy(my_model.dict()))

    test_model["kayit_bilgisi"]["esu_soket_detay"].append(
        Soket(soket_no="Soket3", soket_tip=SoketTipi.AC)
    )

    with pytest.raises(ValidationError) as e:
        ESUKayitModel(**test_model)

    assert str(e.value.errors()[0].get("msg")) is not None


def test_esu_kayit_model_validation_success_case(my_model: ESUKayitModel) -> None:
    """Test successful ESUKayitModel instantiation."""
    try:
        ESUKayitModel(**my_model.dict())
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")


def test_esu_kayit_olustur(my_model: ESUKayitModel) -> None:
    """Test ESUKayit.olustur(firma, esu) class method."""
    firma = Firma(**my_model.dict())

    kayit: ESU = my_model.kayit_bilgisi
    soket_detay = kayit.esu_soket_detay

    soket1 = Soket(**soket_detay[0].dict())

    soket2 = Soket(**soket_detay[1].dict())

    esu = ESU(**kayit.dict())
    esu.esu_soket_detay = [soket1, soket2]

    try:
        ESUKayitModel.olustur(firma=firma, esu=esu)
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
