from enum import Enum
from typing import Annotated, List, Optional

from pydantic import Field, HttpUrl, PositiveInt

from models.api_models import ESUSeriNo, NonEmptyString, TaxNumber, TaxNumberOrEmpty
from models.base_model import CustomBaseModel

# regex patterns

RegEx__Api_Durum_Kodu = r"^\b\d{4}\b$"

# enums


class Durum(str, Enum):
    """Enum for API response status codes."""

    SUCCESS = "success"
    FAILURE = "basarisiz"


class EvetVeyaHayir(str, Enum):
    """Enum for boolean config parameters."""

    EVET = "1"
    HAYIR = "0"


# api response model


class Sonuc(CustomBaseModel):
    """Api result model."""

    esu_seri_no: NonEmptyString
    sira_no: PositiveInt
    kod: str = Field(pattern=RegEx__Api_Durum_Kodu)
    mesaj: str


class Yanit(CustomBaseModel):
    """Api response model."""

    durum: Durum
    sonuc: Annotated[List[Sonuc], Field(default_factory=list, min_length=1)]


# service config models


class API(CustomBaseModel):
    """Service model for API URLs."""

    PROD_API_URL: HttpUrl
    TEST_API_URL: HttpUrl
    ESU_KAYIT_PATH: str
    ESU_MUKELLEF_DURUM_PATH: str
    ESU_GUNCELLEME_PATH: str
    ESU_KAPATMA_PATH: str


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

    FIRMA_UNVAN: NonEmptyString
    EPDK_LISANS_KODU: NonEmptyString
    FIRMA_VKN: TaxNumber
    GIB_FIRMA_KODU: NonEmptyString
    GIB_API_SIFRE: NonEmptyString
    PROD_API: EvetVeyaHayir
    SSL_DOGRULAMA: EvetVeyaHayir
    TEST_FIRMA_KULLAN: EvetVeyaHayir
    GIB_TEST_FIRMA_VKN: TaxNumberOrEmpty


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
