from __future__ import annotations

import re

from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated, TypedDict

# numerical constants
LEN_VKN = 10
LEN_VKN_TCKN = [10, 11]
MIN_FIRMA_KODU = MIN_SERI_NO = LEN_IL_KODU = MIN_LEN_FATURA_ETTN = 3
MIN_LEN_ILCE = MIN_LEN_MUKELLEF_UNVAN = 2

# regex expressions
IL_KODU_REGEX = rf"\b\d{{{LEN_IL_KODU}}}\b"
MUKELLEF_VKN_REGEX = rf"\b\d{{{LEN_VKN}}}\b"
MULKIYET_SAHIBI_VKN_TCKN_REGEX = rf"\b\d{{{','.join(map(str, LEN_VKN_TCKN))}}}\b"
FATURA_TARIHI_I_REGEX = r"^\d{4}-\d{2}-\d{2}$"  # YYYY-MM-DD
FATURA_TARIHI_II_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"  # DD.MM.YYYY

# error messages
FIRMA_KODU_ERROR = f"firma_kodu en az {MIN_FIRMA_KODU} karakter uzunluğunda olmalı"
SERI_NO_ERROR = f"esu_seri_no en az {MIN_SERI_NO} karakter uzunluğunda olmalı"
IL_KODU_ERROR = f"il_kodu {LEN_IL_KODU} karakter uzunluğunda olmalı"
ILCE_ERROR = f"ilçe en az {MIN_LEN_ILCE} karakter uzunluğunda olmalı"
MUKELLEF_VKN_ERROR = f"mukellef_vkn {LEN_VKN} karakter uzunluğunda olmalı"
MUKELLEF_UNVAN_ERROR = (
    "mukellef_unvan en az " f"{MIN_LEN_MUKELLEF_UNVAN} karakter uzunluğunda olmalı"
)
FATURA_ERROR = (
    "fatura_tarihi ve fatura_ettn tutarsız; " "ikisi de boş veya ikisi de dolu olmalı"
)
FATURA_ETTN_ERROR = (
    "fatura_ettn en az " f"{MIN_LEN_FATURA_ETTN} karakter uzunluğunda olmalı"
)
FATURA_TARIHI_ERROR = "fatura_tarihi YYYY-MM-DD \veya DD.MM.YYYY formatında olmalıdır"
MULKİYET_ERROR = (
    "mulkiyet_sahibi_vkn_tckn ve mulkiyet_sahibi_ad_unvan tutarsız; "
    "ikisi de boş veya ikisi de dolu olmalı"
)
MULKIYET_SAHIBI_VKN_TCKN_ERROR = (
    "mulkiyet_sahibi_vkn_tckn "
    f"{' veya '.join(map(str, LEN_VKN_TCKN))} karakter uzunluğunda olmalı"
)
MULKIYET_SAHIBI_AD_UNVAN_ERROR = (
    "mulkiyet_sahibi_ad_unvan en az "
    f"{MIN_LEN_MUKELLEF_UNVAN} karakter uzunluğunda olmalı"
)
SERTIFIKA_ERROR = (
    "sertifika_no ve sertifika_tarihi tutarsız; "
    "ikisi de boş veya ikisi de dolu olmalı"
)
SERTIFIKA_TARIHI_ERROR = "sertifika_tarihi YYYY-MM-DD formatında olmalıdır"
SERTIFIKA_VE_MULKIYET_ERROR = (
    "sertifika bilgilerini gönderebilmek için "
    "mulkiyet_sahibi_vkn_tckn doldurulmalıdır"
)
YA_FATURA_YA_MULKIYET_ERROR = (
    "fatura_ettn veya mulkiyet_sahibi_vkn_tckn "
    "alanlarından biri ve yalnız biri mevcut olmalıdır"
)


class ESUMukellefBilgisi(TypedDict):
    esu_seri_no: str
    il_kodu: str
    ilce: str
    adres_numarası: str
    koordinat: str
    mukellef_vkn: str
    mukellef_unvan: str
    sertifika_no: str
    sertifika_tarihi: str
    fatura_tarihi: str  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu
    fatura_ettn: str  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu
    mulkiyet_sahibi_vkn_tckn: str  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu
    mulkiyet_sahibi_ad_unvan: str  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu


class ESUMukellefModel(TypedDict):
    firma_kodu: str
    durum_bilgileri: ESUMukellefBilgisi


def validate_model(model: ESUMukellefModel) -> ESUMukellefModel:
    firma_kodu = model["firma_kodu"]
    durum = model["durum_bilgileri"]
    seri_no = durum["esu_seri_no"]
    il_kodu = durum["il_kodu"]
    ilce = durum["ilce"]
    mukellef_vkn = durum["mukellef_vkn"]
    mukellef_unvan = durum["mukellef_unvan"]
    sertifika_tarihi = durum.get("sertifika_tarihi", "")
    sertifika_no = durum.get("sertifika_no", "")
    fatura_tarihi = durum.get("fatura_tarihi", "")
    fatura_ettn = durum.get("fatura_ettn", "")
    mulkiyet_sahibi_vkn_tckn = durum.get("mulkiyet_sahibi_vkn_tckn", "")
    mulkiyet_sahibi_ad_unvan = durum.get("mulkiyet_sahibi_ad_unvan", "")

    # conditions to check to enforce consistency and mutual exclusion rules

    mulkiyet_vkn_does_not_exist = len(mulkiyet_sahibi_vkn_tckn.strip()) == 0
    mulkiyet_unvan_does_not_exist = len(mulkiyet_sahibi_ad_unvan.strip()) == 0
    fatura_ettn_does_not_exist = len(fatura_ettn.strip()) == 0
    fatura_tarihi_does_not_exist = len(fatura_tarihi.strip()) == 0
    sertifika_tarihi_does_exist = len(sertifika_tarihi.strip()) > 0
    sertifika_no_does_exist = len(sertifika_no.strip()) > 0

    # enforce consistency between `fatura_ettn` and `fatura_tarihi`
    if fatura_ettn_does_not_exist != fatura_tarihi_does_not_exist:
        raise ValueError(FATURA_ERROR)

    # enforce consistency between
    # `mulkiyet_sahibi_vkn_tckn` and `mulkiyet_sahibi_ad_unvan`
    if mulkiyet_vkn_does_not_exist != mulkiyet_unvan_does_not_exist:
        raise ValueError(MULKİYET_ERROR)

    # enforce consistency between `sertifika_no` and `sertifika_tarihi`
    if sertifika_no_does_exist != sertifika_tarihi_does_exist:
        raise ValueError(SERTIFIKA_ERROR)

    # disallow co-existence or co-absence of
    # `fatura_ettn` and `mulkiyet_sahibi_vkn_tckn`
    if fatura_ettn_does_not_exist == mulkiyet_vkn_does_not_exist:
        raise ValueError(YA_FATURA_YA_MULKIYET_ERROR)

    # allow presence of `sertifika_no` only when `mulkiyet_sahibi_vkn_tckn` is present
    if sertifika_no_does_exist and mulkiyet_vkn_does_not_exist:
        raise ValueError(SERTIFIKA_VE_MULKIYET_ERROR)

    # unconditionally check firma_kodu
    assert len(firma_kodu.strip()) >= MIN_FIRMA_KODU, FIRMA_KODU_ERROR

    # unconditionally check seri_no
    assert len(seri_no.strip()) >= MIN_SERI_NO, SERI_NO_ERROR

    # unconditionally check il_kodu
    assert bool(re.match(IL_KODU_REGEX, il_kodu)), IL_KODU_ERROR

    # unconditionally check ilce
    assert len(ilce.strip()) >= MIN_LEN_ILCE, ILCE_ERROR

    # unconditionally check mukellef_vkn
    assert bool(re.match(MUKELLEF_VKN_REGEX, mukellef_vkn)), MUKELLEF_VKN_ERROR

    # unconditionally check mukellef_unvan
    assert len(mukellef_unvan.strip()) >= MIN_LEN_MUKELLEF_UNVAN, MUKELLEF_UNVAN_ERROR

    # conditionally check fatura_tarihi
    if (
        not fatura_tarihi_does_not_exist
        and not bool(re.match(FATURA_TARIHI_I_REGEX, fatura_tarihi))
        and not bool(re.match(FATURA_TARIHI_II_REGEX, fatura_tarihi))
    ):
        raise ValueError(FATURA_TARIHI_ERROR)

    # conditionally check fatura_ettn
    if (
        not fatura_ettn_does_not_exist
        and len(fatura_ettn.strip()) < MIN_LEN_FATURA_ETTN
    ):
        raise ValueError(FATURA_ETTN_ERROR)

    # conditionally check mulkiyet_sahibi_vkn_tckn
    if not mulkiyet_vkn_does_not_exist and not bool(
        re.match(MULKIYET_SAHIBI_VKN_TCKN_REGEX, mulkiyet_sahibi_vkn_tckn)
    ):
        raise ValueError(MULKIYET_SAHIBI_VKN_TCKN_ERROR)

    # conditionally check mulkiyet_sahibi_ad_unvan
    if (
        not mulkiyet_unvan_does_not_exist
        and len(mulkiyet_sahibi_ad_unvan.strip()) < MIN_LEN_MUKELLEF_UNVAN
    ):
        raise ValueError(MULKIYET_SAHIBI_AD_UNVAN_ERROR)

    # conditionally check sertifika_tarihi
    if sertifika_tarihi_does_exist and not bool(
        re.match(FATURA_TARIHI_I_REGEX, sertifika_tarihi)
    ):
        raise ValueError(SERTIFIKA_TARIHI_ERROR)

    return model


ESUMukellefModelCandidate = Annotated[ESUMukellefModel, AfterValidator(validate_model)]


class ESUMukellef(BaseModel):
    model: ESUMukellefModelCandidate
