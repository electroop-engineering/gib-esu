from __future__ import annotations

import re
from typing import List, Literal

from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated, TypedDict

# numerical constants
LEN_VKN = 10
MIN_FIRMA_KODU = MIN_SERI_NO = 3
MIN_MARKA = MIN_MODEL = 1

# regex expressions
EPDK_LISANS_KODU_REGEX = r"^ŞH/\d{5}-\d+/\d{5}$"
FIRMA_VKN_REGEX = rf"\b\d{{{LEN_VKN}}}\b"
SOKET_SAYISI_REGEX = r"(\d)+"
SOKET_NO_REGEX = r"^Soket\d+$"

# error messages
FIRMA_KODU_ERROR = f"firma_kodu en az {MIN_FIRMA_KODU} karakter uzunluğunda olmalı"
FIRMA_VKN_ERROR = f"firma_vkn {LEN_VKN} karakter uzunluğunda olmalı"
EPDK_LISANS_ERROR = "epdk_lisans_no hatalı"
SERI_NO_ERROR = f"esu_seri_no en az {MIN_SERI_NO} karakter uzunluğunda olmalı"
ESU_MARKA_ERROR = "esu_markasi boş olamaz"
ESU_MODEL_ERROR = "esu_modeli boş olamaz"
SOKET_SAYISI_ERROR = "esu_soket_sayisi 1,2,3 vb. bir sayı olmalı"
SOKET_NO_ERROR = "soket_no hatalı"
SOKET_TIPI_ERROR = "Input should be 'AC', 'DC' or 'AC/DC'"
SOKET_DETAY_TIP_ERROR = "soket detayları esu_soket_tipi ile uyumlu değil"
SOKET_DETAY_UZUNLUK_ERROR = "esu_soket_sayisi kadar soket detayı sağlanmalı"
SOKET_DETAY_ACDC_ERROR = "esu_soket_tipi [AC/DC] soket detayları ile uyumlu değil"


class ESUSoket(TypedDict):
    soket_no: str  # Soket1, Soket2, Soket3, etc.
    soket_tip: Literal["AC", "DC"]


class ESUKayitBilgisi(TypedDict):
    esu_seri_no: str
    esu_soket_tipi: Literal["AC", "DC", "AC/DC"]
    esu_soket_sayisi: str  # "1", "2", "3", etc.
    esu_soket_detay: List[ESUSoket]
    esu_markasi: str
    esu_modeli: str


class ESUKayitModel(TypedDict):
    firma_kodu: str
    firma_vkn: str
    epdk_lisans_no: str
    kayit_bilgisi: ESUKayitBilgisi


def validate_model(model: ESUKayitModel) -> ESUKayitModel:
    firma_kodu = model["firma_kodu"]
    firma_vkn = model["firma_vkn"]
    epdk_no = model["epdk_lisans_no"]
    kayit = model["kayit_bilgisi"]
    seri_no = kayit["esu_seri_no"]
    esu_marka = kayit["esu_markasi"]
    esu_model = kayit["esu_modeli"]
    soket_tipi = kayit["esu_soket_tipi"]
    soket_sayisi = kayit["esu_soket_sayisi"]
    soket_detay = kayit["esu_soket_detay"]

    # unconditionally check firma_kodu
    assert len(firma_kodu.strip()) >= MIN_FIRMA_KODU, FIRMA_KODU_ERROR

    # unconditionally check firma_vkn
    assert bool(re.match(FIRMA_VKN_REGEX, firma_vkn)), FIRMA_VKN_ERROR

    # unconditionally check epdk_lisans_no
    assert bool(re.match(EPDK_LISANS_KODU_REGEX, epdk_no)), EPDK_LISANS_ERROR

    # unconditionally check esu_seri_no
    assert len(seri_no.strip()) >= MIN_SERI_NO, SERI_NO_ERROR

    # unconditionally check esu_markasi
    assert len(esu_marka.strip()) >= MIN_MARKA, ESU_MARKA_ERROR

    # unconditionally check esu_modeli
    assert len(esu_model.strip()) >= MIN_MODEL, ESU_MODEL_ERROR

    # unconditionally check esu_soket_sayisi
    assert bool(re.match(SOKET_SAYISI_REGEX, soket_sayisi)), SOKET_SAYISI_ERROR

    for esu_soket in soket_detay:
        soket_no = esu_soket["soket_no"]
        soket_tip = esu_soket["soket_tip"]
        # check soket_no and soket_tip
        assert bool(re.match(SOKET_NO_REGEX, soket_no)), SOKET_NO_ERROR
        if soket_tipi in ["AC", "DC"] and soket_tip != soket_tipi:
            raise ValueError(SOKET_DETAY_TIP_ERROR)

    # unconditionally check socket count
    assert len(soket_detay) == int(soket_sayisi), SOKET_DETAY_UZUNLUK_ERROR

    # conditionally check socket types
    if soket_tipi == "AC/DC":
        has_ac = any(item["soket_tip"] == "AC" for item in soket_detay)
        has_dc = any(item["soket_tip"] == "DC" for item in soket_detay)
        assert has_ac and has_dc, SOKET_DETAY_ACDC_ERROR
    return model


ESUKayitModelCandidate = Annotated[ESUKayitModel, AfterValidator(validate_model)]


class ESUKayit(BaseModel):
    model: ESUKayitModelCandidate
