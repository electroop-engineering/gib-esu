from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from .constants import (
    ERROR_SOKET_DETAY_ACDC,
    ERROR_SOKET_DETAY_TIP,
    ERROR_SOKET_DETAY_UZUNLUK,
    F_KAYIT_BILGISI,
    LEN_VKN,
    MIN_FIRMA_KODU,
    MIN_FIRMA_UNVAN,
    MIN_MARKA,
    MIN_MODEL,
    MIN_SERI_NO,
    REGEX_EPDK_LISANS_KODU,
    REGEX_FIRMA_VKN,
    REGEX_SOKET_NO,
    REGEX_SOKET_SAYISI,
    STR_AC,
    STR_AC_DC,
    STR_DC,
)


class SoketTipi(str, Enum):
    AC = STR_AC
    DC = STR_DC


class ESUSoketTipi(str, Enum):
    AC = STR_AC
    DC = STR_DC
    AC_DC = STR_AC_DC


class Soket(BaseModel):
    soket_no: str = Field(pattern=REGEX_SOKET_NO)  # Soket1, Soket2, Soket3, etc.
    soket_tip: SoketTipi


class ESU(BaseModel):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)
    esu_soket_tipi: ESUSoketTipi
    esu_soket_sayisi: str = Field(pattern=REGEX_SOKET_SAYISI)  # "1", "2", "3", etc.
    esu_soket_detay: Annotated[List[Soket], Field(min_length=1)]
    esu_markasi: str = Field(min_length=MIN_MARKA)
    esu_modeli: str = Field(min_length=MIN_MODEL)


class Firma(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    firma_vkn: str = Field(
        min_length=LEN_VKN, max_length=LEN_VKN, pattern=REGEX_FIRMA_VKN
    )
    firma_unvan: str = Field(min_length=MIN_FIRMA_UNVAN)
    epdk_lisans_no: str = Field(pattern=REGEX_EPDK_LISANS_KODU)


class ESUKayitModel(Firma):
    kayit_bilgisi: ESU


def check_model_constraints(model: ESUKayitModel) -> ESUKayitModel:
    kayit: ESU = model.kayit_bilgisi
    soket_tipi = kayit.esu_soket_tipi
    soket_sayisi = kayit.esu_soket_sayisi
    soket_detay = kayit.esu_soket_detay

    for esu_soket in soket_detay:
        soket_tip = esu_soket.soket_tip
        if soket_tipi in [STR_AC, STR_DC] and soket_tip != soket_tipi:
            raise ValueError(ERROR_SOKET_DETAY_TIP)

    # unconditionally check socket count
    assert len(soket_detay) == int(soket_sayisi), ERROR_SOKET_DETAY_UZUNLUK

    # conditionally check socket types
    if soket_tipi == STR_AC_DC:
        has_ac = any(item.soket_tip == STR_AC for item in soket_detay)
        has_dc = any(item.soket_tip == STR_DC for item in soket_detay)
        assert has_ac and has_dc, ERROR_SOKET_DETAY_ACDC
    return model


ESUKayitModelCandidate = Annotated[
    ESUKayitModel, AfterValidator(check_model_constraints)
]


class ESUKayit(BaseModel):
    model: ESUKayitModelCandidate

    @classmethod
    def olustur(cls, firma: Firma, esu: ESU) -> ESUKayit:
        combined_data = {**firma.__dict__, F_KAYIT_BILGISI: esu}
        model_instance = ESUKayitModel(**combined_data)
        return cls(model=model_instance)
