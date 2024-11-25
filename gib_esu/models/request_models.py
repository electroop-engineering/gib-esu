from __future__ import annotations

import re
from enum import Enum
from typing import Annotated, List, Optional, TypeVar, Union, cast

from pydantic import (
    AfterValidator,
    Field,
    PlainValidator,
    StringConstraints,
    model_validator,
)
from typing_extensions import Self

from gib_esu.models.base_model import CustomBaseModel

# regex patterns

RegEx__Soket_No = r"^Soket\d+$"
RegEx__Soket_Sayisi = r"^[1-9]$"
RegEx__Firma_VKN = r"\b\d{10}\b"
RegEx__Il_Kodu = r"\b\d{3}\b"
RegEx__Tarih = r"^\d{4}-\d{2}-\d{2}$"  # YYYY-MM-DD


# validators
def _validate_tax_number(tax_nr: str) -> str:
    """Validates a given tax number.

    Args:
        tax_nr (str): Tax number to validate

    Raises:
        ValueError: In case tax_nr does not conform to tax number scheme

    Returns:
        str: Validated tax_nr
    """
    v_str = tax_nr.strip()
    if not v_str or re.fullmatch(RegEx__Firma_VKN, v_str):
        return v_str
    raise ValueError(f"{tax_nr} geçerli bir vergi kimlik numarası değil")


def _validate_tax_payer_and_update_models(model: CustomBaseModelWithValidator) -> None:
    """Validates both the tax payer registration and the charge point update models."""
    durum: Union[ESUMukellefBilgisi, ESUGuncellemeBilgisi] = (
        cast(ESUGuncellemeModel, model).guncelleme_istek_bilgileri
        if isinstance(model, ESUGuncellemeModel)
        else cast(ESUMukellefModel, model).durum_bilgileri
    )
    sertifika_tarihi = durum.sertifika_tarihi or ""
    sertifika_no = durum.sertifika_no or ""
    fatura_tarihi = durum.fatura_tarihi or ""
    fatura_ettn = durum.fatura_ettn or ""
    mulkiyet_sahibi_vkn_tckn = durum.mulkiyet_sahibi_vkn_tckn or ""
    mulkiyet_sahibi_ad_unvan = durum.mulkiyet_sahibi_ad_unvan or ""

    # conditions to check to enforce consistency and mutual exclusion rules

    mulkiyet_vkn_does_not_exist = len(mulkiyet_sahibi_vkn_tckn.strip()) == 0
    mulkiyet_unvan_does_not_exist = len(mulkiyet_sahibi_ad_unvan.strip()) == 0
    fatura_ettn_does_not_exist = len(fatura_ettn.strip()) == 0
    fatura_tarihi_does_not_exist = len(fatura_tarihi.strip()) == 0
    sertifika_tarihi_does_exist = len(sertifika_tarihi.strip()) > 0
    sertifika_no_does_exist = len(sertifika_no.strip()) > 0

    # enforce consistency between `fatura_ettn` and `fatura_tarihi`
    if fatura_ettn_does_not_exist != fatura_tarihi_does_not_exist:
        raise ValueError(
            (
                "`fatura_tarihi` ile `fatura_ettn` tutarsız; "
                "ikisi de boş veya ikisi de dolu olmalı"
            )
        )

    # enforce consistency between
    # `mulkiyet_sahibi_vkn_tckn` and `mulkiyet_sahibi_ad_unvan`
    if mulkiyet_vkn_does_not_exist != mulkiyet_unvan_does_not_exist:
        raise ValueError(
            (
                "`mulkiyet_sahibi_vkn_tckn` ile `mulkiyet_sahibi_ad_unvan` tutarsız; "
                "ikisi de boş veya ikisi de dolu olmalı"
            )
        )

    # enforce consistency between `sertifika_no` and `sertifika_tarihi`
    if sertifika_no_does_exist != sertifika_tarihi_does_exist:
        raise ValueError(
            "`sertifika_no` ile `sertifika_tarihi` tutarsız; "
            "ikisi de boş veya ikisi de dolu olmalı"
        )

    # disallow co-existence or co-absence of
    # `fatura_ettn` and `mulkiyet_sahibi_vkn_tckn`
    if fatura_ettn_does_not_exist == mulkiyet_vkn_does_not_exist:
        raise ValueError(
            (
                "`fatura_ettn` veya `mulkiyet_sahibi_vkn_tckn` "
                "alanlarından biri ve yalnız biri mevcut olmalıdır"
            )
        )

    # allow presence of `sertifika_no` only when `mulkiyet_sahibi_vkn_tckn` is present
    """ if sertifika_no_does_exist and mulkiyet_vkn_does_not_exist:
        raise ValueError(
            "sertifika bilgilerini gönderebilmek için "
            "`mulkiyet_sahibi_vkn_tckn` dolu olmalıdır"
        ) """

    # conditionally check fatura_tarihi
    if not fatura_tarihi_does_not_exist and not bool(
        re.match(RegEx__Tarih, fatura_tarihi)
    ):
        raise ValueError("`fatura_tarihi` YYYY-MM-DD formatında olmalıdır")

    # conditionally check sertifika_tarihi
    if sertifika_tarihi_does_exist and not bool(
        re.match(RegEx__Tarih, sertifika_tarihi)
    ):
        raise ValueError("`sertifika_tarihi` YYYY-MM-DD formatında olmalıdır")


# type definitions

T = TypeVar("T")

"""Type definition of a non-empty string."""
NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True),
    AfterValidator(lambda v: v),
    StringConstraints(min_length=1),
]

"""Type definition of a non-empty list."""
NonEmptyList = Annotated[List[T], Field(default_factory=list, min_length=1)]


"""Type definition for required tax numbers."""
TaxNumber = Annotated[
    str,
    StringConstraints(strip_whitespace=True),
    Field(pattern=RegEx__Firma_VKN),
]


"""Type definition for optional tax numbers."""
TaxNumberOrEmpty = Annotated[
    str,
    StringConstraints(strip_whitespace=True),
    PlainValidator(_validate_tax_number),
]

"""Type definition for city code."""
CityCode = Annotated[
    str, StringConstraints(strip_whitespace=True), Field(pattern=RegEx__Il_Kodu)
]

# enums


class SoketTipi(str, Enum):
    """Socket type enum."""

    AC = "AC"
    DC = "DC"


class ESUTipi(str, Enum):
    """Charge point type enum."""

    AC = SoketTipi.AC.value
    DC = SoketTipi.DC.value
    AC_DC = "AC/DC"


# domain models


class Soket(CustomBaseModel):
    """Charge point's connectors."""

    soket_no: str = Field(pattern=RegEx__Soket_No)  # Soket1, Soket2, Soket3, etc.
    soket_tip: SoketTipi


class ESUSeriNo(CustomBaseModel):
    """Charge point's serial number."""

    esu_seri_no: NonEmptyString


class ESU(ESUSeriNo):
    """Charge point model."""

    esu_soket_tipi: ESUTipi
    esu_soket_sayisi: str = Field(pattern=RegEx__Soket_Sayisi)  # "1", "2", "3", etc.
    esu_soket_detay: NonEmptyList[Soket]
    esu_markasi: NonEmptyString
    esu_modeli: NonEmptyString


class FirmaKodu(CustomBaseModel):
    """Company code model."""

    firma_kodu: NonEmptyString


class Firma(FirmaKodu):
    """Company info model."""

    firma_vkn: TaxNumber
    epdk_lisans_no: NonEmptyString
    firma_unvan: Optional[NonEmptyString] = Field(default=None, exclude=True)


class Lokasyon(CustomBaseModel):
    """EV charging location model."""

    il_kodu: CityCode
    ilce: NonEmptyString
    adres_numarası: Optional[str] = ""
    koordinat: Optional[str] = ""


class Mukellef(CustomBaseModel):
    """Tax payer model."""

    mukellef_vkn: Optional[TaxNumberOrEmpty] = ""
    mukellef_unvan: Optional[str] = ""


class Sertifika(CustomBaseModel):
    """Certificate model."""

    sertifika_no: Optional[str] = ""
    sertifika_tarihi: Optional[str] = ""


class Fatura(CustomBaseModel):
    """Invoice model."""

    fatura_tarihi: Optional[str] = ""
    fatura_ettn: Optional[str] = ""


class MulkiyetSahibi(CustomBaseModel):
    """Charge point owner model."""

    mulkiyet_sahibi_vkn_tckn: Optional[TaxNumberOrEmpty] = ""
    mulkiyet_sahibi_ad_unvan: Optional[str] = ""


class ESUMukellefBilgisi(
    ESUSeriNo, Fatura, Lokasyon, Mukellef, MulkiyetSahibi, Sertifika
):
    """Intermediary model that encapsulates charge point and tax payer information."""

    pass


class ESUGuncellemeBilgisi(ESUSeriNo, Fatura, Lokasyon, MulkiyetSahibi, Sertifika):
    """Intermediary model that encapsulates charge point and ownership information."""

    pass


class CustomBaseModelWithValidator(CustomBaseModel):
    """Custom base model with a predefined model validator function."""

    @model_validator(mode="after")
    def _enforce_model_constraints(self) -> Self:
        """Validates the model according to the model constraints."""
        _validate_tax_payer_and_update_models(cast(CustomBaseModelWithValidator, self))
        return self


# request models


class ESUKayitModel(Firma):
    """Charge point registration request model."""

    kayit_bilgisi: ESU

    @classmethod
    def olustur(cls, firma: Firma, esu: ESU) -> ESUKayitModel:
        """Constructs a ESUKayitModel from given `esu` and `firma` arguments.

        Args:
            firma (Firma): Company information
            esu (ESU): Charge point information

        Returns:
            ESUKayitModel: Constructed model instance
        """
        combined_data = {**firma.__dict__, "kayit_bilgisi": esu}
        return ESUKayitModel(**combined_data)

    @model_validator(mode="after")
    def _enforce_model_constraints(self) -> Self:
        """Validates the model according to the model constraints."""
        kayit: ESU = self.kayit_bilgisi
        soket_tipi = kayit.esu_soket_tipi
        soket_sayisi = kayit.esu_soket_sayisi
        soket_detay = kayit.esu_soket_detay

        # check socket type integrity
        for esu_soket in soket_detay:
            soket_tip = esu_soket.soket_tip
            if soket_tipi in SoketTipi.__members__.values() and soket_tip != soket_tipi:
                raise ValueError("Soket detayları `esu_soket_tipi` ile uyumlu değil")

        # compare socket count to socket details length
        assert len(soket_detay) == int(
            soket_sayisi
        ), "`esu_soket_sayisi` kadar `esu_soket_detay` olmalı"

        # check socket details when charge point type is AC/DC
        if soket_tipi == ESUTipi.AC_DC.value:
            has_ac = any(item.soket_tip == SoketTipi.AC.value for item in soket_detay)
            has_dc = any(item.soket_tip == SoketTipi.DC.value for item in soket_detay)
            assert has_ac and has_dc, "Soket detayları AC/DC EŞÜ ile uyumlu değil"
        return self


class ESUKapatmaModel(CustomBaseModel):
    """Charge point delisting request model."""

    firma_kodu: NonEmptyString
    kapatma_bilgisi: ESUSeriNo


class ESUMukellefModel(CustomBaseModelWithValidator, FirmaKodu):
    """Charge point tax payer info registration model."""

    durum_bilgileri: ESUMukellefBilgisi

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
    ) -> ESUMukellefModel:
        """Constructs a ESUMukellefModel from given arguments.

        Args:
            esu_seri_no (str): Charge point serial number
            firma_kodu (str): Company code
            fatura (Fatura): Invoice information
            lokasyon (Lokasyon): Location information
            mukellef (Mukellef): Tax payer information
            mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
            Ownership information. Defaults to None.
            sertifika (Optional[Sertifika], optional): Certificate. Defaults to None.

        Returns:
            ESUMukellefModel: Constructed model instance
        """
        combined_data = {
            **ESUSeriNo(esu_seri_no=esu_seri_no).model_dump(),
            **fatura.model_dump(),
            **lokasyon.model_dump(),
            **mukellef.model_dump(),
            **(mulkiyet_sahibi or MulkiyetSahibi()).model_dump(),
            **(sertifika or Sertifika()).model_dump(),
        }
        mukellef_durum = ESUMukellefBilgisi(**combined_data)
        return ESUMukellefModel(
            **FirmaKodu(firma_kodu=firma_kodu).model_dump(),
            durum_bilgileri=mukellef_durum,
        )


class ESUGuncellemeModel(CustomBaseModelWithValidator, FirmaKodu):
    """Charge point update request model."""

    guncelleme_istek_bilgileri: ESUGuncellemeBilgisi

    @classmethod
    def olustur(
        cls,
        esu_seri_no: ESUSeriNo,
        firma_kodu: str,
        fatura: Fatura,
        lokasyon: Lokasyon,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> ESUGuncellemeModel:
        """Constructs a ESUGuncellemeModel from given arguments.

        Args:
            esu_seri_no (str): Charge point serial number
            firma_kodu (str): Company code
            fatura (Fatura): Invoice information
            lokasyon (Lokasyon): Location information
            mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
            Ownership information. Defaults to None.
            sertifika (Optional[Sertifika], optional): Certificate. Defaults to None.

        Returns:
            ESUGuncellemeModel: Constructed model instance
        """
        combined_data = {
            **esu_seri_no.model_dump(),
            **fatura.model_dump(),
            **lokasyon.model_dump(),
            **(mulkiyet_sahibi or MulkiyetSahibi()).model_dump(),
            **(sertifika or Sertifika()).model_dump(),
        }

        return ESUGuncellemeModel(
            **FirmaKodu(firma_kodu=firma_kodu).model_dump(),
            guncelleme_istek_bilgileri=ESUGuncellemeBilgisi(**combined_data),
        )
