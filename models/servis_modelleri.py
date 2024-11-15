from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, PositiveInt

from models.constants import (
    LEN_KOD,
    MIN_FIRMA_KODU,
    MIN_FIRMA_UNVAN,
    MIN_SERI_NO,
    MIN_SIFRE,
    REGEX_API_KOD,
    REGEX_EPDK_LISANS_KODU,
    REGEX_FIRMA_VKN,
    STR_API_BASARI,
    STR_API_HATA,
    STR_BIR,
    STR_SIFIR,
)


class Durum(str, Enum):
    SUCCESS = STR_API_BASARI
    FAILURE = STR_API_HATA


class Sonuc(BaseModel):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)
    sira_no: PositiveInt
    kod: str = Field(min_length=LEN_KOD, max_length=LEN_KOD, pattern=REGEX_API_KOD)
    mesaj: str


class Yanit(BaseModel):
    durum: Durum
    sonuc: List[Sonuc]


class DoğruVeyaYanlış(str, Enum):
    YANLIŞ = STR_SIFIR
    DOĞRU = STR_BIR


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
    FIRMA_UNVAN: str = Field(min_length=MIN_FIRMA_UNVAN)
    EPDK_LISANS_KODU: str = Field(pattern=REGEX_EPDK_LISANS_KODU)
    FIRMA_VKN: str = Field(pattern=REGEX_FIRMA_VKN)
    GIB_FIRMA_KODU: str = Field(min_length=MIN_FIRMA_KODU)
    GIB_API_SIFRE: str = Field(min_length=MIN_SIFRE)
    PROD_API: DoğruVeyaYanlış
    SSL_DOGRULAMA: DoğruVeyaYanlış
    TEST_FIRMA_KULLAN: DoğruVeyaYanlış
    GIB_TEST_FIRMA_VKN: str = Field(pattern=REGEX_FIRMA_VKN)


class ESUKayitSonucu(BaseModel):
    esu_kayit_sonucu: str


class MukellefKayitSonucu(BaseModel):
    mukellef_kayit_sonucu: str


class ESUTopluKayitSonucu(ESUKayitSonucu, MukellefKayitSonucu):
    esu_seri_no: str = Field(min_length=MIN_SERI_NO)


class TopluKayitSonuc(BaseModel):
    sonuclar: List[ESUTopluKayitSonucu]
    toplam: int
