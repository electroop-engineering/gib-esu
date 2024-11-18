import base64
import concurrent.futures
import io
import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

import requests
from dotenv import dotenv_values
from pydantic import HttpUrl

from helpers.py_utils import PyUtils
from models.api_models import (
    ESU,
    ESUGuncellemeModel,
    ESUKapatmaModel,
    ESUKayitModel,
    ESUMukellefModel,
    ESUSeriNo,
    Fatura,
    Firma,
    Lokasyon,
    Mukellef,
    MulkiyetSahibi,
    Sertifika,
    Soket,
)
from models.service_models import (
    APIParametreleri,
    ESUServisKonfigurasyonu,
    ESUTopluGuncellemeSonucu,
    ESUTopluKayitSonucu,
    EvetVeyaHayir,
    TopluGuncellemeSonuc,
    TopluKayitSonuc,
    Yanit,
)


class ESUServis:

    DEFAULT_ENV = ".env"

    class API(str, Enum):
        PROD = "https://okc.gib.gov.tr/api/v1/okc/okcesu"
        TEST = "https://okctest.gib.gov.tr/api/v1/okc/okcesu"

    class ISTEK_TIPI(str, Enum):
        ESU_KAYIT = "/yeniEsuKayit"
        ESU_MUKELLEF = "/esuMukellefDurum"
        ESU_GUNCELLEME = "/esuGuncelleme"
        ESU_KAPATMA = "/esuKapatma"

    def __init__(self, _config: Optional[Dict[str, str | None]] = None) -> None:
        _cfg = dotenv_values(ESUServis.DEFAULT_ENV) if _config is None else _config
        config = ESUServisKonfigurasyonu.model_validate(_cfg)
        self._api = APIParametreleri(
            api_sifre=str(config.GIB_API_SIFRE),
            prod_api=config.PROD_API == EvetVeyaHayir.EVET,
            ssl_dogrulama=str(config.SSL_DOGRULAMA) == EvetVeyaHayir.EVET,
            test_firma=config.TEST_FIRMA_KULLAN == EvetVeyaHayir.EVET,
            test_firma_vkn=config.GIB_TEST_FIRMA_VKN,
        )
        self._firma = Firma(
            firma_kodu=config.GIB_FIRMA_KODU,
            firma_vkn=(
                config.FIRMA_VKN
                if not self._api.test_firma
                else self._api.test_firma_vkn
            ),
            firma_unvan=config.FIRMA_UNVAN,
            epdk_lisans_no=config.EPDK_LISANS_KODU,
        )
        self._api.api_url = (
            cast(HttpUrl, ESUServis.API.PROD)
            if self._api.prod_api
            else cast(HttpUrl, ESUServis.API.TEST)
        )
        # ssl_dogrulama `0` (False) ise SSL ile ilgili uyarı mesajları gösterilmez
        if not self._api.ssl_dogrulama:
            import urllib3
            from urllib3.exceptions import InsecureRequestWarning

            urllib3.disable_warnings(InsecureRequestWarning)

    def _api_isteği(
        self, data: Any, istek_tipi: ISTEK_TIPI = ISTEK_TIPI.ESU_KAYIT
    ) -> Yanit:
        token = f"{self._firma.firma_kodu}:{self._api.api_sifre}".encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64.b64encode(token).decode('utf-8')}",
        }
        url = f"{self._api.api_url}{istek_tipi}"
        response = requests.post(
            url=url,
            headers=headers,
            json=data,
            verify=self._api.ssl_dogrulama,
        )
        return Yanit.model_validate_json(json_data=json.dumps(response.json()))

    def cihaz_kayit(self, cihaz_bilgileri: Union[ESUKayitModel, ESU]) -> Yanit:
        cihaz = (
            cihaz_bilgileri
            if isinstance(cihaz_bilgileri, ESUKayitModel)
            else ESUKayitModel.olustur(
                firma=self._firma,
                esu=cihaz_bilgileri,
            )
        )
        return self._api_isteği(cihaz.model_dump())

    def mukellef_kayit(
        self,
        mukellef_bilgileri: Union[ESUMukellefModel, Any] = None,
        esu: Optional[ESU] = None,
        lokasyon: Optional[Lokasyon] = None,
        fatura: Optional[Fatura] = None,
        mukellef: Optional[Mukellef] = None,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> Yanit:
        veri: Optional[ESUMukellefModel] = None
        if not isinstance(mukellef_bilgileri, ESUMukellefModel):
            if (
                not esu
                or not lokasyon
                or not mukellef
                or not (fatura or mulkiyet_sahibi)
            ):
                raise ValueError("Mükellef bilgileri eksik")

            _fatura = (
                fatura
                if fatura is not None
                else Fatura(fatura_tarihi="", fatura_ettn="")
            )
            _mukellef = (
                mukellef
                if mukellef is not None
                else Mukellef(
                    mukellef_vkn=self._firma.firma_vkn,
                    mukellef_unvan=str(self._firma.firma_unvan),
                )
            )
            _mulkiyet_sahibi = (
                mulkiyet_sahibi
                if mulkiyet_sahibi is not None
                else MulkiyetSahibi(
                    mulkiyet_sahibi_vkn_tckn="", mulkiyet_sahibi_ad_unvan=""
                )
            )
            _sertifika = (
                sertifika
                if sertifika is not None
                else Sertifika(sertifika_no="", sertifika_tarihi="")
            )
            veri = ESUMukellefModel.olustur(
                esu_seri_no=ESUSeriNo(**esu.model_dump()),
                firma_kodu=self._firma.firma_kodu,
                fatura=_fatura,
                lokasyon=lokasyon,
                mukellef=_mukellef,
                mulkiyet_sahibi=_mulkiyet_sahibi,
                sertifika=_sertifika,
            )
        elif isinstance(mukellef_bilgileri, ESUMukellefModel):
            veri = mukellef_bilgileri

        return self._api_isteği(
            veri.model_dump(), istek_tipi=ESUServis.ISTEK_TIPI.ESU_MUKELLEF
        )

    def _esu_bilgisi_hazirla(self, kayit: dict) -> ESU:
        soket_detay = [
            Soket(soket_no=pair.split(":")[0], soket_tip=pair.split(":")[1])
            for pair in kayit["esu_soket_detay"].split(";")
        ]

        return ESU(
            esu_seri_no=kayit["esu_seri_no"],
            esu_soket_tipi=kayit["esu_soket_tipi"],
            esu_soket_sayisi=kayit["esu_soket_sayisi"],
            esu_soket_detay=soket_detay,
            esu_markasi=kayit["esu_markasi"],
            esu_modeli=kayit["esu_modeli"],
        )

    def _mukellef_bilgisi_hazirla(self, kayit: dict, esu: ESU) -> ESUMukellefModel:
        lokasyon = Lokasyon(**kayit)
        if kayit.get("mukellef_vkn") and kayit.get("mukellef_unvan"):
            mukellef = Mukellef(**kayit)
        else:
            mukellef = Mukellef(
                mukellef_vkn=self._firma.firma_vkn,
                mukellef_unvan=self._firma.firma_unvan,
            )
        fatura = (
            Fatura(**kayit) if not kayit.get("mulkiyet_sahibi_vkn_tckn") else Fatura()
        )
        sertifika = Sertifika(**kayit) if not kayit.get("fatura_ettn") else Sertifika()
        mulkiyet = (
            MulkiyetSahibi(**kayit)
            if not kayit.get("fatura_ettn")
            else MulkiyetSahibi()
        )

        return ESUMukellefModel.olustur(
            esu_seri_no=ESUSeriNo(**esu.model_dump()),
            firma_kodu=self._firma.firma_kodu,
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
            mulkiyet_sahibi=mulkiyet,
            sertifika=sertifika,
        )

    def _kayit_isle(self, kayit: dict, sonuc: TopluKayitSonuc) -> None:
        esu = self._esu_bilgisi_hazirla(kayit)
        esu_yanit = self.cihaz_kayit(esu)
        mukellef = self._mukellef_bilgisi_hazirla(kayit, esu)
        mukellef_yanit = self.mukellef_kayit(mukellef)
        sonuc.sonuclar.append(
            ESUTopluKayitSonucu(
                esu_seri_no=esu.esu_seri_no,
                esu_kayit_sonucu=esu_yanit.sonuc[0].mesaj,
                mukellef_kayit_sonucu=mukellef_yanit.sonuc[0].mesaj,
            )
        )

    def _dosyaya_yaz(self, cikti_dosya_yolu: str, icerik: str) -> None:
        with open(cikti_dosya_yolu, "w") as f:
            f.write(icerik)

    def toplu_kayit(
        self,
        giris_dosya_yolu: Optional[str] = None,
        csv_string: Optional[io.StringIO] = None,
        dosyaya_yaz: Optional[bool] = None,
        cikti_dosya_yolu: Optional[str] = None,
        paralel: Optional[bool] = None,
    ) -> dict[str, Any]:
        csv_path = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "data"
            / "esu_list.csv"
        )
        records = PyUtils.read_csv_input(giris_dosya_yolu or csv_string or csv_path)
        print(f"{giris_dosya_yolu or csv_path} csv giriş dosyası okundu")

        sonuc = TopluKayitSonuc(sonuclar=[], toplam=0)

        print("GİB'e gönderim başlıyor...")

        if bool(paralel):

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max((os.cpu_count() or 6) - 2, 1)
            ) as executor:
                futures = [
                    executor.submit(self._kayit_isle, dict(record), sonuc)
                    for _, record in records.iterrows()
                ]
                concurrent.futures.wait(
                    futures, return_when=concurrent.futures.ALL_COMPLETED
                )

        else:
            for _, record in records.iterrows():
                self._kayit_isle(dict(record), sonuc)

        sonuc.toplam = len(sonuc.sonuclar)

        if bool(dosyaya_yaz):
            self._dosyaya_yaz(
                cikti_dosya_yolu=(cikti_dosya_yolu or "gonderim_raporu.json"),
                icerik=sonuc.model_dump_json(indent=4),
            )

        return sonuc.model_dump()

    def kayit_guncelle(
        self,
        kayit_bilgileri: Union[ESUGuncellemeModel, Any] = None,
        esu_seri_no: Optional[str] = None,
        lokasyon: Optional[Lokasyon] = None,
        fatura: Optional[Fatura] = None,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> Yanit:
        veri: Optional[ESUGuncellemeModel] = None
        if not isinstance(kayit_bilgileri, ESUGuncellemeModel):
            if not esu_seri_no or not lokasyon or not (fatura or mulkiyet_sahibi):
                raise ValueError("Kayıt bilgileri eksik")

            _fatura = (
                fatura
                if fatura is not None
                else Fatura(fatura_tarihi="", fatura_ettn="")
            )
            _mulkiyet_sahibi = (
                mulkiyet_sahibi
                if mulkiyet_sahibi is not None
                else MulkiyetSahibi(
                    mulkiyet_sahibi_vkn_tckn="", mulkiyet_sahibi_ad_unvan=""
                )
            )
            _sertifika = (
                sertifika
                if sertifika is not None
                else Sertifika(sertifika_no="", sertifika_tarihi="")
            )
            veri = ESUGuncellemeModel.olustur(
                esu_seri_no=ESUSeriNo(esu_seri_no=esu_seri_no),
                firma_kodu=self._firma.firma_kodu,
                fatura=_fatura,
                lokasyon=lokasyon,
                mulkiyet_sahibi=_mulkiyet_sahibi,
                sertifika=_sertifika,
            )
        elif isinstance(kayit_bilgileri, ESUGuncellemeModel):
            veri = kayit_bilgileri

        return self._api_isteği(
            veri.model_dump(), istek_tipi=ESUServis.ISTEK_TIPI.ESU_GUNCELLEME
        )

    def _guncelleme_kaydi_isle(self, kayit: dict, sonuc: TopluGuncellemeSonuc) -> None:

        guncelleme_yanit = self.kayit_guncelle(
            esu_seri_no=kayit["esu_seri_no"],
            lokasyon=Lokasyon(**kayit),
            fatura=(
                Fatura(**kayit)
                if not kayit.get("mulkiyet_sahibi_vkn_tckn")
                else Fatura()
            ),
            sertifika=(
                Sertifika(**kayit) if not kayit.get("fatura_ettn") else Sertifika()
            ),
            mulkiyet_sahibi=(
                MulkiyetSahibi(**kayit)
                if not kayit.get("fatura_ettn")
                else MulkiyetSahibi()
            ),
        )
        sonuc.sonuclar.append(
            ESUTopluGuncellemeSonucu(
                esu_seri_no=kayit["esu_seri_no"],
                guncelleme_kayit_sonucu=guncelleme_yanit.sonuc[0].mesaj,
            )
        )

    def toplu_guncelle(
        self,
        giris_dosya_yolu: Optional[str] = None,
        csv_string: Optional[io.StringIO] = None,
        dosyaya_yaz: Optional[bool] = None,
        cikti_dosya_yolu: Optional[str] = None,
        paralel: Optional[bool] = None,
    ) -> dict[str, Any]:
        csv_path = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "data"
            / "esu_list.csv"
        )
        records = PyUtils.read_csv_input(giris_dosya_yolu or csv_string or csv_path)
        print(f"{giris_dosya_yolu or csv_path} csv giriş dosyası okundu")

        sonuc = TopluGuncellemeSonuc(sonuclar=[], toplam=0)

        print("GİB'e gönderim başlıyor...")

        if bool(paralel):

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max((os.cpu_count() or 6) - 2, 1)
            ) as executor:
                futures = [
                    executor.submit(self._guncelleme_kaydi_isle, dict(record), sonuc)
                    for _, record in records.iterrows()
                ]
                concurrent.futures.wait(
                    futures, return_when=concurrent.futures.ALL_COMPLETED
                )

        else:
            for _, record in records.iterrows():
                self._guncelleme_kaydi_isle(dict(record), sonuc)

        sonuc.toplam = len(sonuc.sonuclar)

        if bool(dosyaya_yaz):
            self._dosyaya_yaz(
                cikti_dosya_yolu=(cikti_dosya_yolu or "gonderim_raporu.json"),
                icerik=sonuc.model_dump_json(indent=4),
            )

        return sonuc.model_dump()

    def cihaz_kapatma(
        self,
        cihaz_bilgisi: Optional[ESUKapatmaModel] = None,
        esu_seri_no: Optional[ESUSeriNo] = None,
    ) -> Yanit:
        cihaz = (
            cihaz_bilgisi
            if isinstance(cihaz_bilgisi, ESUKapatmaModel)
            else ESUKapatmaModel(
                firma_kodu=self._firma.firma_kodu,
                kapatma_bilgisi=cast(ESUSeriNo, esu_seri_no),
            )
        )
        return self._api_isteği(
            cihaz.model_dump(), istek_tipi=ESUServis.ISTEK_TIPI.ESU_KAPATMA
        )
