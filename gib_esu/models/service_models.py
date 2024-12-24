import re
from enum import Enum
from typing import List, Optional

from gib_esu.models.base_model import CustomBaseModel
from gib_esu.models.request_models import ESUSeriNo, RegEx__Firma_VKN
from pydantic import HttpUrl, constr, root_validator

# enums


class EvetVeyaHayir(str, Enum):
    """Enum for boolean config parameters."""

    EVET = "1"
    HAYIR = "0"


# service config models


class APIParametreleri(CustomBaseModel):
    """Service model for API parameters."""

    api_sifre: str
    test_firma_vkn: str
    test_firma: bool
    prod_api: bool
    ssl_dogrulama: bool
    api_url: Optional[HttpUrl] = None


class ESUServisKonfigurasyonu(CustomBaseModel):
    """Service configuration model."""

    FIRMA_UNVAN: constr(strip_whitespace=True, min_length=1)  # type: ignore
    EPDK_LISANS_KODU: constr(strip_whitespace=True, min_length=1)  # type: ignore
    FIRMA_VKN: constr(strip_whitespace=True, regex=RegEx__Firma_VKN)  # type: ignore
    GIB_FIRMA_KODU: constr(strip_whitespace=True, min_length=1)  # type: ignore
    GIB_API_SIFRE: constr(strip_whitespace=True, min_length=1)  # type: ignore
    PROD_API: EvetVeyaHayir
    SSL_DOGRULAMA: EvetVeyaHayir
    TEST_FIRMA_KULLAN: EvetVeyaHayir
    GIB_TEST_FIRMA_VKN: str = ""

    @root_validator(pre=True)
    def validate_field(cls, values):
        value = values.get("GIB_TEST_FIRMA_VKN", "").strip()
        if value and not re.fullmatch(RegEx__Firma_VKN, value):
            raise ValueError("Invalid tax number")
        return values

# service output models


class ESUKayitSonucu(CustomBaseModel):
    """Charge point registration output model."""

    esu_kayit_sonucu: str


class MukellefKayitSonucu(CustomBaseModel):
    """Charge point tax payer registration model."""

    mukellef_kayit_sonucu: str


class ESUTopluKayitSonucu(ESUSeriNo, ESUKayitSonucu, MukellefKayitSonucu):
    """Batch registration output model for single charge point."""

    pass


class TopluKayitSonuc(CustomBaseModel):
    """Charge point batch registration output model."""

    sonuclar: List[ESUTopluKayitSonucu]
    toplam: int


class ESUTopluGuncellemeSonucu(ESUSeriNo):
    """Batch update output model for single charge point."""

    guncelleme_kayit_sonucu: str


class TopluGuncellemeSonuc(CustomBaseModel):
    """Charge point batch update output model."""

    sonuclar: List[ESUTopluGuncellemeSonucu]
    toplam: int
