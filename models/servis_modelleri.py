from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, PositiveInt


class Durum(str, Enum):
    SUCCESS = "success"
    FAILURE = "basarisiz"


class Sonuc(BaseModel):
    esu_seri_no: str = Field(min_length=3)
    sira_no: PositiveInt
    kod: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
    mesaj: str


class Yanit(BaseModel):
    durum: Durum
    sonuc: List[Sonuc]


class DoğruVeyaYanlış(str, Enum):
    YANLIŞ = "0"
    DOĞRU = "1"


class APIParametreleri(BaseModel):
    api_sifre: str
    test_firma_vkn: str
    test_firma: bool
    prod_api: bool
    ssl_dogrulama: bool
    api_url: Optional[HttpUrl] = None


class Sabitler(BaseModel):
    PROD_API_URL: HttpUrl
    TEST_API_URL: HttpUrl
    ESU_KAYIT_PATH: str
    ESU_MUKELLEF_DURUM_PATH: str
    ESU_GUNCELLEME_PATH: str
    ESU_KAPATMA_PATH: str


class ESUServisParametreleri(BaseModel):
    FIRMA_UNVAN: str = Field(min_length=3)
    EPDK_LISANS_KODU: str = Field(pattern=r"^ŞH/\d{5}-\d+/\d{5}$")
    FIRMA_VKN: str = Field(pattern=r"\b\d{10}\b")
    GIB_FIRMA_KODU: str = Field(min_length=3)
    GIB_API_SIFRE: str = Field(min_length=6)
    PROD_API: DoğruVeyaYanlış
    SSL_DOGRULAMA: DoğruVeyaYanlış
    TEST_FIRMA_KULLAN: DoğruVeyaYanlış
    GIB_TEST_FIRMA_VKN: str = Field(pattern=r"\b\d{10}\b")


class ESUKayitSonucu(BaseModel):
    esu_kayit_sonucu: str


class MukellefKayitSonucu(BaseModel):
    mukellef_kayit_sonucu: str


class ESUTopluKayitSonucu(ESUKayitSonucu, MukellefKayitSonucu):
    esu_seri_no: str = Field(min_length=3)


class TopluKayitSonuc(BaseModel):
    sonuclar: List[ESUTopluKayitSonucu]
    toplam: int
