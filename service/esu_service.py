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
from models.constants import (
    ERROR_MUKELLEF_EKSIK,
    F_ESU_SERI_NO,
    F_FATURA_ETTN,
    F_FATURA_TARIHI,
    F_IL_KODU,
    F_ILCE,
    F_MARKA,
    F_MODEL,
    F_MUKELLEF_UNVAN,
    F_MUKELLEF_VKN,
    F_MULKIYET_UNVAN,
    F_MULKİYET_VKN,
    F_SERTIFIKA_NO,
    F_SERTIFIKA_TARIHI,
    F_SOKET_DETAY,
    F_SOKET_SAYISI,
    F_SOKET_TIPI,
    STR_BOS,
)
from models.esu_kayit import ESU, ESUKayit, Firma, Soket
from models.esu_mukellef import (
    ESUMukellef,
    Fatura,
    Lokasyon,
    Mukellef,
    MulkiyetSahibi,
    Sertifika,
)
from models.servis_modelleri import (
    APIParametreleri,
    DoğruVeyaYanlış,
    ESUServisParametreleri,
    ESUTopluKayitSonucu,
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
        config = ESUServisParametreleri.model_validate(_cfg)
        self._api = APIParametreleri(
            api_sifre=config.GIB_API_SIFRE,
            prod_api=config.PROD_API == DoğruVeyaYanlış.DOĞRU,
            ssl_dogrulama=config.SSL_DOGRULAMA == DoğruVeyaYanlış.DOĞRU,
            test_firma=config.TEST_FIRMA_KULLAN == DoğruVeyaYanlış.DOĞRU,
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

    def cihaz_kayit(self, cihaz_bilgileri: Union[ESUKayit, ESU]) -> Yanit:
        cihaz = (
            cihaz_bilgileri
            if isinstance(cihaz_bilgileri, ESUKayit)
            else ESUKayit.olustur(
                firma=self._firma,
                esu=cihaz_bilgileri,
            )
        )
        return self._api_isteği(cihaz.model.model_dump())

    def mukellef_kayit(
        self,
        mukellef_bilgileri: Union[ESUMukellef, Any] = None,
        esu: Optional[ESU] = None,
        lokasyon: Optional[Lokasyon] = None,
        fatura: Optional[Fatura] = None,
        mukellef: Optional[Mukellef] = None,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> Yanit:
        veri: Optional[ESUMukellef] = None
        if not isinstance(mukellef_bilgileri, ESUMukellef):
            if (
                not esu
                or not lokasyon
                or not mukellef
                or not (fatura or mulkiyet_sahibi)
            ):
                raise ValueError(ERROR_MUKELLEF_EKSIK)
            _esu_seri_no = esu.esu_seri_no

            _fatura = (
                fatura
                if fatura is not None
                else Fatura(fatura_tarihi=STR_BOS, fatura_ettn=STR_BOS)
            )
            _mukellef = (
                mukellef
                if mukellef is not None
                else Mukellef(
                    mukellef_vkn=self._firma.firma_vkn,
                    mukellef_unvan=self._firma.firma_unvan,
                )
            )
            _mulkiyet_sahibi = (
                mulkiyet_sahibi
                if mulkiyet_sahibi is not None
                else MulkiyetSahibi(
                    mulkiyet_sahibi_vkn_tckn=STR_BOS, mulkiyet_sahibi_ad_unvan=STR_BOS
                )
            )
            _sertifika = (
                sertifika
                if sertifika is not None
                else Sertifika(sertifika_no=STR_BOS, sertifika_tarihi=STR_BOS)
            )
            veri = ESUMukellef.olustur(
                esu_seri_no=_esu_seri_no,
                firma_kodu=self._firma.firma_kodu,
                fatura=_fatura,
                lokasyon=lokasyon,
                mukellef=_mukellef,
                mulkiyet_sahibi=_mulkiyet_sahibi,
                sertifika=_sertifika,
            )
        elif isinstance(mukellef_bilgileri, ESUMukellef):
            veri = mukellef_bilgileri

        return self._api_isteği(
            veri.model.model_dump(), istek_tipi=ESUServis.ISTEK_TIPI.ESU_MUKELLEF
        )

    def _esu_bilgisi_hazirla(self, kayit: dict) -> ESU:
        soket_detay = [
            Soket(soket_no=pair.split(":")[0], soket_tip=pair.split(":")[1])
            for pair in kayit[F_SOKET_DETAY].split(";")
        ]

        return ESU(
            esu_seri_no=kayit[F_ESU_SERI_NO],
            esu_soket_tipi=kayit[F_SOKET_TIPI],
            esu_soket_sayisi=kayit[F_SOKET_SAYISI],
            esu_soket_detay=soket_detay,
            esu_markasi=kayit[F_MARKA],
            esu_modeli=kayit[F_MODEL],
        )

    def _mukellef_bilgisi_hazirla(self, kayit: dict, esu: ESU) -> ESUMukellef:
        lokasyon = Lokasyon(
            il_kodu=kayit[F_IL_KODU],
            ilce=kayit[F_ILCE],
            adres_numarası=STR_BOS,
            koordinat=STR_BOS,
        )

        mukellef = Mukellef(
            mukellef_vkn=(
                PyUtils.pad_with_zeroes(kayit[F_MUKELLEF_VKN])
                if kayit.get(F_MUKELLEF_VKN)
                else self._firma.firma_vkn
            ),
            mukellef_unvan=(
                kayit[F_MUKELLEF_UNVAN]
                if kayit.get(F_MUKELLEF_UNVAN)
                else self._firma.firma_unvan
            ),
        )

        fatura = Fatura(
            fatura_tarihi=(
                kayit[F_FATURA_TARIHI]
                if not kayit.get(F_MULKİYET_VKN) and kayit[F_FATURA_TARIHI]
                else STR_BOS
            ),
            fatura_ettn=(
                kayit[F_FATURA_ETTN] if not kayit.get(F_MULKİYET_VKN) else STR_BOS
            ),
        )

        sertifika = Sertifika(
            sertifika_no=(
                kayit[F_SERTIFIKA_NO] if kayit.get(F_SERTIFIKA_NO) else STR_BOS
            ),
            sertifika_tarihi=(
                kayit[F_SERTIFIKA_TARIHI] if kayit.get(F_SERTIFIKA_TARIHI) else STR_BOS
            ),
        )

        mulkiyet = MulkiyetSahibi(
            mulkiyet_sahibi_vkn_tckn=(
                PyUtils.pad_with_zeroes(kayit[F_MULKİYET_VKN])
                if kayit.get(F_MULKİYET_VKN)
                else STR_BOS
            ),
            mulkiyet_sahibi_ad_unvan=(
                kayit[F_MULKIYET_UNVAN] if kayit.get(F_MULKIYET_UNVAN) else STR_BOS
            ),
        )

        return ESUMukellef.olustur(
            esu_seri_no=esu.esu_seri_no,
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
