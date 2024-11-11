from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

# numerical constants
LEN_VKN = 10
MIN_FIRMA_KODU = MIN_SERI_NO = MIN_FIRMA_UNVAN = 3
MIN_MARKA = MIN_MODEL = 1

# regex expressions
EPDK_LISANS_KODU_REGEX = r"^ŞH/\d{5}-\d+/\d{5}$"
FIRMA_VKN_REGEX = rf"\b\d{{{LEN_VKN}}}\b"
SOKET_SAYISI_REGEX = r"^\d+$"
SOKET_NO_REGEX = r"^Soket\d+$"

# error messages
SOKET_DETAY_TIP_ERROR = "soket detayları esu_soket_tipi ile uyumlu değil"
SOKET_DETAY_UZUNLUK_ERROR = "esu_soket_sayisi kadar soket detayı sağlanmalı"
SOKET_DETAY_ACDC_ERROR = "esu_soket_tipi [AC/DC] soket detayları ile uyumlu değil"


class SoketTipi(str, Enum):
    AC = "AC"
    DC = "DC"


class ESUSoketTipi(str, Enum):
    AC = "AC"
    DC = "DC"
    AC_DC = "AC/DC"


class Soket(BaseModel):
    soket_no: str = Field(pattern=SOKET_NO_REGEX)  # Soket1, Soket2, Soket3, etc.
    soket_tip: SoketTipi


class ESU(BaseModel):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)
    esu_soket_tipi: ESUSoketTipi
    esu_soket_sayisi: str = Field(pattern=SOKET_SAYISI_REGEX)  # "1", "2", "3", etc.
    esu_soket_detay: Annotated[List[Soket], Field(min_length=1)]
    esu_markasi: str = Field(min_length=MIN_MARKA)
    esu_modeli: str = Field(min_length=MIN_MODEL)


class Firma(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    firma_vkn: str = Field(
        min_length=LEN_VKN, max_length=LEN_VKN, pattern=FIRMA_VKN_REGEX
    )
    firma_unvan: str = Field(min_length=MIN_FIRMA_UNVAN)
    epdk_lisans_no: str = Field(pattern=EPDK_LISANS_KODU_REGEX)


class ESUKayitModel(Firma):
    kayit_bilgisi: ESU


def check_model_constraints(model: ESUKayitModel) -> ESUKayitModel:
    kayit: ESU = model.kayit_bilgisi
    soket_tipi = kayit.esu_soket_tipi
    soket_sayisi = kayit.esu_soket_sayisi
    soket_detay = kayit.esu_soket_detay

    for esu_soket in soket_detay:
        soket_tip = esu_soket.soket_tip
        if soket_tipi in ["AC", "DC"] and soket_tip != soket_tipi:
            raise ValueError(SOKET_DETAY_TIP_ERROR)

    # unconditionally check socket count
    assert len(soket_detay) == int(soket_sayisi), SOKET_DETAY_UZUNLUK_ERROR

    # conditionally check socket types
    if soket_tipi == "AC/DC":
        has_ac = any(item.soket_tip == "AC" for item in soket_detay)
        has_dc = any(item.soket_tip == "DC" for item in soket_detay)
        assert has_ac and has_dc, SOKET_DETAY_ACDC_ERROR
    return model


ESUKayitModelCandidate = Annotated[
    ESUKayitModel, AfterValidator(check_model_constraints)
]


class ESUKayit(BaseModel):
    model: ESUKayitModelCandidate

    @classmethod
    def olustur(cls, firma: Firma, esu: ESU) -> ESUKayit:
        combined_data = {**firma.__dict__, "kayit_bilgisi": esu}
        model_instance = ESUKayitModel(**combined_data)
        return cls(model=model_instance)
