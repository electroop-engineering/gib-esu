from __future__ import annotations

import re
from typing import Optional, Union, cast

from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

# numerical constants
LEN_VKN = 10
LEN_VKN_TCKN = [10, 11]
MIN_FIRMA_KODU = MIN_SERI_NO = LEN_IL_KODU = MIN_LEN_FATURA_ETTN = 3
MIN_LEN_ILCE = MIN_LEN_MUKELLEF_UNVAN = 2

# regex expressions
IL_KODU_REGEX = rf"\b\d{{{LEN_IL_KODU}}}\b"
MUKELLEF_VKN_REGEX = rf"\b\d{{{LEN_VKN}}}\b"
MULKIYET_SAHIBI_VKN_TCKN_REGEX = rf"\b\d{{{','.join(map(str, LEN_VKN_TCKN))}}}\b"
TARIH_REGEX = r"^\d{4}-\d{2}-\d{2}$"  # YYYY-MM-DD

# error messages
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
FATURA_TARIHI_ERROR = "fatura_tarihi YYYY-MM-DD formatında olmalıdır"
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


class Lokasyon(BaseModel):
    il_kodu: str = Field(
        min_length=LEN_IL_KODU, max_length=LEN_IL_KODU, pattern=IL_KODU_REGEX
    )
    ilce: str = Field(min_length=MIN_LEN_ILCE)
    adres_numarası: str
    koordinat: str


class Mukellef(BaseModel):
    mukellef_vkn: str
    mukellef_unvan: str


class Sertifika(BaseModel):
    sertifika_no: str
    sertifika_tarihi: str


class Fatura(BaseModel):
    fatura_tarihi: str  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu
    fatura_ettn: str  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu


class MulkiyetSahibi(BaseModel):
    mulkiyet_sahibi_vkn_tckn: str  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu
    mulkiyet_sahibi_ad_unvan: str  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu


class ESUMukellefBilgisi(Fatura, Lokasyon, Mukellef, MulkiyetSahibi, Sertifika):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)


class ESUMukellefModel(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    durum_bilgileri: ESUMukellefBilgisi


class ESUGuncellemeBilgisi(Fatura, Lokasyon, MulkiyetSahibi, Sertifika):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)


class ESUGuncellemeModel(BaseModel):
    firma_kodu: str = Field(min_length=MIN_FIRMA_KODU)
    guncelleme_istek_bilgileri: ESUGuncellemeBilgisi


def validate_model(
    model: Union[ESUMukellefModel, ESUGuncellemeModel]
) -> Union[ESUMukellefModel, ESUGuncellemeModel]:
    durum: Union[ESUMukellefBilgisi, ESUGuncellemeBilgisi] = (
        model.guncelleme_istek_bilgileri
        if isinstance(model, ESUGuncellemeModel)
        else model.durum_bilgileri
    )
    sertifika_tarihi = durum.sertifika_tarihi
    sertifika_no = durum.sertifika_no
    fatura_tarihi = durum.fatura_tarihi
    fatura_ettn = durum.fatura_ettn
    mulkiyet_sahibi_vkn_tckn = durum.mulkiyet_sahibi_vkn_tckn
    mulkiyet_sahibi_ad_unvan = durum.mulkiyet_sahibi_ad_unvan

    if isinstance(durum, ESUMukellefBilgisi):
        mukellef_vkn = durum.mukellef_vkn
        mukellef_unvan = durum.mukellef_unvan

        # unconditionally check mukellef_vkn
        assert bool(re.match(MUKELLEF_VKN_REGEX, mukellef_vkn)), MUKELLEF_VKN_ERROR

        # unconditionally check mukellef_unvan
        assert (
            len(mukellef_unvan.strip()) >= MIN_LEN_MUKELLEF_UNVAN
        ), MUKELLEF_UNVAN_ERROR

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

    # conditionally check fatura_tarihi
    if not fatura_tarihi_does_not_exist and not bool(
        re.match(TARIH_REGEX, fatura_tarihi)
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
        re.match(TARIH_REGEX, sertifika_tarihi)
    ):
        raise ValueError(SERTIFIKA_TARIHI_ERROR)

    return model


ESUMukellefModelCandidate = Annotated[ESUMukellefModel, AfterValidator(validate_model)]
ESUGuncellemeModelCandidate = Annotated[
    ESUGuncellemeModel, AfterValidator(validate_model)
]


class ESUMukellef(BaseModel):
    model: ESUMukellefModelCandidate

    @classmethod
    def olustur(
        cls,
        esu_seri_no: str,
        firma_kodu: str,
        fatura: Fatura,
        lokasyon: Lokasyon,
        mukellef: Mukellef,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> ESUMukellef:
        mukellef_durum = ESUMukellefBilgisi(
            esu_seri_no=esu_seri_no,
            fatura_ettn=fatura.fatura_ettn,
            fatura_tarihi=fatura.fatura_tarihi,
            adres_numarası=lokasyon.adres_numarası,
            koordinat=lokasyon.koordinat,
            il_kodu=lokasyon.il_kodu,
            ilce=lokasyon.ilce,
            mukellef_vkn=mukellef.mukellef_vkn,
            mukellef_unvan=mukellef.mukellef_unvan,
            mulkiyet_sahibi_vkn_tckn=(
                mulkiyet_sahibi.mulkiyet_sahibi_vkn_tckn if mulkiyet_sahibi else ""
            ),
            mulkiyet_sahibi_ad_unvan=(
                mulkiyet_sahibi.mulkiyet_sahibi_ad_unvan if mulkiyet_sahibi else ""
            ),
            sertifika_no=sertifika.sertifika_no if sertifika else "",
            sertifika_tarihi=sertifika.sertifika_tarihi if sertifika else "",
        )
        data = {"firma_kodu": firma_kodu, "durum_bilgileri": mukellef_durum}
        return cls(model=cast(ESUMukellefModelCandidate, data))


class ESUGuncelleme(BaseModel):
    model: ESUGuncellemeModelCandidate

    @classmethod
    def olustur(
        cls,
        esu_seri_no: str,
        firma_kodu: str,
        fatura: Fatura,
        lokasyon: Lokasyon,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> ESUGuncelleme:
        mukellef_durum = ESUGuncellemeBilgisi(
            esu_seri_no=esu_seri_no,
            fatura_ettn=fatura.fatura_ettn,
            fatura_tarihi=fatura.fatura_tarihi,
            adres_numarası=lokasyon.adres_numarası,
            koordinat=lokasyon.koordinat,
            il_kodu=lokasyon.il_kodu,
            ilce=lokasyon.ilce,
            mulkiyet_sahibi_vkn_tckn=(
                mulkiyet_sahibi.mulkiyet_sahibi_vkn_tckn if mulkiyet_sahibi else ""
            ),
            mulkiyet_sahibi_ad_unvan=(
                mulkiyet_sahibi.mulkiyet_sahibi_ad_unvan if mulkiyet_sahibi else ""
            ),
            sertifika_no=sertifika.sertifika_no if sertifika else "",
            sertifika_tarihi=sertifika.sertifika_tarihi if sertifika else "",
        )
        data = {"firma_kodu": firma_kodu, "guncelleme_istek_bilgileri": mukellef_durum}
        return cls(model=cast(ESUGuncellemeModelCandidate, data))
