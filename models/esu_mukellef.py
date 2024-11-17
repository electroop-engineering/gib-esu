from __future__ import annotations

import re
from typing import Optional, Union, cast

from pydantic import BaseModel, Field, field_validator
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from helpers.py_utils import PyUtils

from .sabitler import (
    ERROR_FATURA,
    ERROR_FATURA_ETTN,
    ERROR_FATURA_TARIHI,
    ERROR_MUKELLEF_UNVAN,
    ERROR_MUKELLEF_VKN,
    ERROR_MULKIYET_SAHIBI_AD_UNVAN,
    ERROR_MULKIYET_SAHIBI_VKN_TCKN,
    ERROR_MULKİYET,
    ERROR_SERTIFIKA,
    ERROR_SERTIFIKA_TARIHI,
    ERROR_SERTIFIKA_VE_MULKIYET,
    ERROR_YA_FATURA_YA_MULKIYET,
    F_DURUM_BILGILERI,
    F_FIRMA_KODU,
    F_GUNCELLEME_BILGILERI,
    LEN_IL_KODU,
    MIN_FIRMA_KODU,
    MIN_LEN_FATURA_ETTN,
    MIN_LEN_ILCE,
    MIN_LEN_MUKELLEF_UNVAN,
    MIN_SERI_NO,
    REGEX_FIRMA_VKN,
    REGEX_IL_KODU,
    REGEX_MULKIYET_SAHIBI_VKN_TCKN,
    REGEX_TARIH,
    STR_BOS,
    CustomBaseModel,
)


class Lokasyon(CustomBaseModel):
    il_kodu: str = Field(
        min_length=LEN_IL_KODU, max_length=LEN_IL_KODU, pattern=REGEX_IL_KODU
    )
    ilce: str = Field(min_length=MIN_LEN_ILCE)
    adres_numarası: Optional[str] = STR_BOS
    koordinat: Optional[str] = STR_BOS


class Mukellef(CustomBaseModel):
    mukellef_vkn: str = STR_BOS
    mukellef_unvan: str = STR_BOS

    @field_validator("mukellef_vkn", mode="before")
    @classmethod
    def left_pad_zeroes_till_ten(cls, v: str) -> str:
        return PyUtils.pad_with_zeroes(v) if v else STR_BOS


class Sertifika(CustomBaseModel):
    sertifika_no: str = STR_BOS
    sertifika_tarihi: str = STR_BOS


class Fatura(CustomBaseModel):
    fatura_tarihi: str = STR_BOS  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu
    fatura_ettn: str = STR_BOS  # Mülkiyet sahibi, lokasyon SAHİBİ ise dolu


class MulkiyetSahibi(CustomBaseModel):
    mulkiyet_sahibi_vkn_tckn: str = (
        STR_BOS  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu
    )
    mulkiyet_sahibi_ad_unvan: str = (
        STR_BOS  # Mülkiyet sahibi, lokasyon SAHİBİ değilse dolu
    )

    @field_validator("mulkiyet_sahibi_vkn_tckn", mode="before")
    @classmethod
    def left_pad_zeroes_till_ten(cls, v: str) -> str:
        return PyUtils.pad_with_zeroes(v) if v else STR_BOS


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
        assert bool(re.match(REGEX_FIRMA_VKN, mukellef_vkn)), ERROR_MUKELLEF_VKN

        # unconditionally check mukellef_unvan
        assert (
            len(mukellef_unvan.strip()) >= MIN_LEN_MUKELLEF_UNVAN
        ), ERROR_MUKELLEF_UNVAN

    # conditions to check to enforce consistency and mutual exclusion rules

    mulkiyet_vkn_does_not_exist = len(mulkiyet_sahibi_vkn_tckn.strip()) == 0
    mulkiyet_unvan_does_not_exist = len(mulkiyet_sahibi_ad_unvan.strip()) == 0
    fatura_ettn_does_not_exist = len(fatura_ettn.strip()) == 0
    fatura_tarihi_does_not_exist = len(fatura_tarihi.strip()) == 0
    sertifika_tarihi_does_exist = len(sertifika_tarihi.strip()) > 0
    sertifika_no_does_exist = len(sertifika_no.strip()) > 0

    # enforce consistency between `fatura_ettn` and `fatura_tarihi`
    if fatura_ettn_does_not_exist != fatura_tarihi_does_not_exist:
        raise ValueError(ERROR_FATURA)

    # enforce consistency between
    # `mulkiyet_sahibi_vkn_tckn` and `mulkiyet_sahibi_ad_unvan`
    if mulkiyet_vkn_does_not_exist != mulkiyet_unvan_does_not_exist:
        raise ValueError(ERROR_MULKİYET)

    # enforce consistency between `sertifika_no` and `sertifika_tarihi`
    if sertifika_no_does_exist != sertifika_tarihi_does_exist:
        raise ValueError(ERROR_SERTIFIKA)

    # disallow co-existence or co-absence of
    # `fatura_ettn` and `mulkiyet_sahibi_vkn_tckn`
    if fatura_ettn_does_not_exist == mulkiyet_vkn_does_not_exist:
        raise ValueError(ERROR_YA_FATURA_YA_MULKIYET)

    # allow presence of `sertifika_no` only when `mulkiyet_sahibi_vkn_tckn` is present
    if sertifika_no_does_exist and mulkiyet_vkn_does_not_exist:
        raise ValueError(ERROR_SERTIFIKA_VE_MULKIYET)

    # conditionally check fatura_tarihi
    if not fatura_tarihi_does_not_exist and not bool(
        re.match(REGEX_TARIH, fatura_tarihi)
    ):
        raise ValueError(ERROR_FATURA_TARIHI)

    # conditionally check fatura_ettn
    if (
        not fatura_ettn_does_not_exist
        and len(fatura_ettn.strip()) < MIN_LEN_FATURA_ETTN
    ):
        raise ValueError(ERROR_FATURA_ETTN)

    # conditionally check mulkiyet_sahibi_vkn_tckn
    if not mulkiyet_vkn_does_not_exist and not bool(
        re.match(REGEX_MULKIYET_SAHIBI_VKN_TCKN, mulkiyet_sahibi_vkn_tckn)
    ):
        raise ValueError(ERROR_MULKIYET_SAHIBI_VKN_TCKN)

    # conditionally check mulkiyet_sahibi_ad_unvan
    if (
        not mulkiyet_unvan_does_not_exist
        and len(mulkiyet_sahibi_ad_unvan.strip()) < MIN_LEN_MUKELLEF_UNVAN
    ):
        raise ValueError(ERROR_MULKIYET_SAHIBI_AD_UNVAN)

    # conditionally check sertifika_tarihi
    if sertifika_tarihi_does_exist and not bool(
        re.match(REGEX_TARIH, sertifika_tarihi)
    ):
        raise ValueError(ERROR_SERTIFIKA_TARIHI)

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
                mulkiyet_sahibi.mulkiyet_sahibi_vkn_tckn if mulkiyet_sahibi else STR_BOS
            ),
            mulkiyet_sahibi_ad_unvan=(
                mulkiyet_sahibi.mulkiyet_sahibi_ad_unvan if mulkiyet_sahibi else STR_BOS
            ),
            sertifika_no=sertifika.sertifika_no if sertifika else STR_BOS,
            sertifika_tarihi=sertifika.sertifika_tarihi if sertifika else STR_BOS,
        )
        data = {F_FIRMA_KODU: firma_kodu, F_DURUM_BILGILERI: mukellef_durum}
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
                mulkiyet_sahibi.mulkiyet_sahibi_vkn_tckn if mulkiyet_sahibi else STR_BOS
            ),
            mulkiyet_sahibi_ad_unvan=(
                mulkiyet_sahibi.mulkiyet_sahibi_ad_unvan if mulkiyet_sahibi else STR_BOS
            ),
            sertifika_no=sertifika.sertifika_no if sertifika else STR_BOS,
            sertifika_tarihi=sertifika.sertifika_tarihi if sertifika else STR_BOS,
        )
        data = {F_FIRMA_KODU: firma_kodu, F_GUNCELLEME_BILGILERI: mukellef_durum}
        return cls(model=cast(ESUGuncellemeModelCandidate, data))
