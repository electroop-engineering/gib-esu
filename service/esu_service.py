import base64
import json
from enum import Enum
from pathlib import Path
from time import sleep
from typing import Any, Dict, Optional, Union, cast

import requests
from dotenv import dotenv_values
from pydantic import HttpUrl

from helpers.py_utils import PyUtils
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

    class API(str, Enum):
        PROD = "https://okc.gib.gov.tr/api/v1/okc/okcesu"
        TEST = "https://okctest.gib.gov.tr/api/v1/okc/okcesu"

    class ISTEK_TIPI(str, Enum):
        ESU_KAYIT = "/yeniEsuKayit"
        ESU_MUKELLEF = "/esuMukellefDurum"
        ESU_GUNCELLEME = "/esuGuncelleme"
        ESU_KAPATMA = "/esuKapatma"

    def __init__(self, _config: Optional[Dict[str, str | None]] = None) -> None:
        _cfg = dotenv_values(".env") if _config is None else _config
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
                raise ValueError("Mükellef bilgileri eksik")
            _esu_seri_no = esu.esu_seri_no

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
                    mukellef_unvan=self._firma.firma_unvan,
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

    def _mukellef_bilgisi_hazirla(self, kayit: dict, esu: ESU) -> ESUMukellef:
        lokasyon = Lokasyon(
            il_kodu=kayit["il_kodu"],
            ilce=kayit["ilce"],
            adres_numarası="",
            koordinat="",
        )

        mukellef = Mukellef(
            mukellef_vkn=(
                PyUtils.pad_with_zeroes(kayit["mukellef_vkn"])
                if kayit.get("mukellef_vkn")
                else self._firma.firma_vkn
            ),
            mukellef_unvan=(
                kayit["mukellef_unvan"]
                if kayit.get("mukellef_unvan")
                else self._firma.firma_unvan
            ),
        )

        fatura = Fatura(
            fatura_tarihi=(
                kayit["fatura_tarihi"]
                if not kayit.get("mulkiyet_vkn") and kayit["fatura_tarihi"]
                else ""
            ),
            fatura_ettn=(kayit["fatura_ettn"] if not kayit.get("mulkiyet_vkn") else ""),
        )

        sertifika = Sertifika(
            sertifika_no=(kayit["sertifika_no"] if kayit.get("sertifika_no") else ""),
            sertifika_tarihi=(
                kayit["sertifika_tarihi"] if kayit.get("sertifika_tarihi") else ""
            ),
        )

        mulkiyet = MulkiyetSahibi(
            mulkiyet_sahibi_vkn_tckn=(
                PyUtils.pad_with_zeroes(kayit["mulkiyet_vkn"])
                if kayit.get("mulkiyet_vkn")
                else ""
            ),
            mulkiyet_sahibi_ad_unvan=(
                kayit["mulkiyet_unvan"] if kayit.get("mulkiyet_unvan") else ""
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

    def _kayit_isle(self, kayit: dict) -> ESUTopluKayitSonucu:
        esu = self._esu_bilgisi_hazirla(kayit)
        esu_yanit = self.cihaz_kayit(esu)
        sleep(
            2
        )  # ikinci istekten önce 2 saniye bekle, GİB'in cihazı kaydettiğinden emin ol
        mukellef = self._mukellef_bilgisi_hazirla(kayit, esu)
        mukellef_yanit = self.mukellef_kayit(mukellef)
        return ESUTopluKayitSonucu(
            esu_seri_no=esu.esu_seri_no,
            esu_kayit_sonucu=esu_yanit.sonuc[0].mesaj,
            mukellef_kayit_sonucu=mukellef_yanit.sonuc[0].mesaj,
        )

    def toplu_kayit(
        self,
        giris_dosya_yolu: Optional[str] = None,
        cikti_dosya_yolu: str = "gonderim_raporu.json",
    ) -> dict[str, Any]:
        csv_path = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "data"
            / "esu_list.csv"
        )
        records = PyUtils.read_csv_input(giris_dosya_yolu or csv_path)
        print(f"{giris_dosya_yolu or csv_path} csv giriş dosyası okundu")

        sonuc = TopluKayitSonuc(sonuclar=[], toplam=0)

        print("GİB'e gönderim başlıyor...")

        for _index, record in records.iterrows():
            kayit_sonucu = self._kayit_isle(dict(record))
            sonuc.sonuclar.append(kayit_sonucu)
            sonuc.toplam += 1

        with open(cikti_dosya_yolu, "w") as f:
            f.write(sonuc.model_dump_json(indent=4))

        return sonuc.model_dump()
