import base64
import concurrent.futures
import io
import json
import logging
import os
from enum import Enum
from typing import Any, Dict, Optional, Union, cast

import requests
from dotenv import dotenv_values
from gib_esu.helpers.py_utils import PyUtils
from gib_esu.models.request_models import (ESU, ESUGuncellemeModel,
                                           ESUKapatmaModel, ESUKayitModel,
                                           ESUMukellefModel, ESUSeriNo, Fatura,
                                           Firma, Lokasyon, Mukellef,
                                           MulkiyetSahibi, Sertifika, Soket)
from gib_esu.models.response_models import Yanit
from gib_esu.models.service_models import (APIParametreleri,
                                           ESUServisKonfigurasyonu,
                                           ESUTopluGuncellemeSonucu,
                                           ESUTopluKayitSonucu, EvetVeyaHayir,
                                           TopluGuncellemeSonuc,
                                           TopluKayitSonuc)
from pydantic import HttpUrl


class ESUServis:
    """Class that handles GIB ESU EKS service operations."""

    # name of the default environment file to read the configuration
    _DEFAULT_ENV = ".env"

    class _API(str, Enum):
        """Enum for available GIB ESU EKS service base urls."""

        PROD = "https://okc.gib.gov.tr/api/v1/okc/okcesu"
        TEST = "https://okctest.gib.gov.tr/api/v1/okc/okcesu"

    class _ISTEK_TIPI(str, Enum):
        """Enum for available GIB ESU EKS service paths."""

        ESU_KAYIT = "/yeniEsuKayit"
        ESU_MUKELLEF = "/esuMukellefDurum"
        ESU_GUNCELLEME = "/esuGuncelleme"
        ESU_KAPATMA = "/esuKapatma"

    def __init__(self, _config: Optional[Dict[str, str | None]] = None) -> None:
        """ESUServis constructor.

        Args:
            _config (Optional[Dict[str, str  |  None]], optional):
            Dictionary or env file path to read the config from. Defaults to None.
        """
        _cfg = dotenv_values(ESUServis._DEFAULT_ENV) if _config is None else _config
        config = ESUServisKonfigurasyonu.parse_obj(_cfg)
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
            cast(HttpUrl, ESUServis._API.PROD)
            if self._api.prod_api
            else cast(HttpUrl, ESUServis._API.TEST)
        )
        # no ssl warnings will be displayed when `ssl_dogrulama` is set to `0` (False)
        if not self._api.ssl_dogrulama:
            import urllib3
            from urllib3.exceptions import InsecureRequestWarning

            urllib3.disable_warnings(InsecureRequestWarning)

        # configure logging
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()  # console logger
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _api_isteği(
        self, data: Any, istek_tipi: _ISTEK_TIPI = _ISTEK_TIPI.ESU_KAYIT
    ) -> Yanit:
        """Internal method to perform API requests.

        Returns:
            Yanit: GIB ESU EKS service reponse
        """

        # construct basic auth header
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
        return Yanit.parse_raw(json.dumps(response.json()))

    def cihaz_kayit(self, cihaz_bilgileri: Union[ESUKayitModel, ESU]) -> Yanit:
        """Registers a charge point with the GIB ESU EKS system.

        Args:
            cihaz_bilgileri (Union[ESUKayitModel, ESU]): Charge point information

        Returns:
            Yanit: GIB ESU EKS service reponse
        """
        cihaz = (
            cihaz_bilgileri
            if isinstance(cihaz_bilgileri, ESUKayitModel)
            else ESUKayitModel.olustur(
                firma=self._firma,
                esu=cihaz_bilgileri,
            )
        )
        self.logger.debug(cihaz.json())
        return self._api_isteği(cihaz.dict())

    def mukellef_kayit(
        self,
        mukellef_bilgileri: Union[ESUMukellefModel, Any] = None,
        esu: Optional[Union[ESU, str]] = None,
        lokasyon: Optional[Lokasyon] = None,
        fatura: Optional[Fatura] = None,
        mukellef: Optional[Mukellef] = None,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> Yanit:
        """Registers tax payer information for a charge point identified by `esu`.

        Args:
            mukellef_bilgileri (Union[ESUMukellefModel, Any], optional):
                Tax payer request model. Defaults to None.
            esu (Optional[Union[ESU, str]], optional):
                Charge point information. Defaults to None.
            lokasyon (Optional[Lokasyon], optional):
                Location information. Defaults to None.
            fatura (Optional[Fatura], optional):
                Invoice information. Defaults to None.
            mukellef (Optional[Mukellef], optional):
                Tax payer information. Defaults to None.
            mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
                Ownership information. Defaults to None.
            sertifika (Optional[Sertifika], optional):
                Certificate information. Defaults to None.

        Raises:
            ValueError: When some information is missing to construct the request model

        Returns:
            Yanit: GIB ESU EKS service reponse
        """
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
                esu_seri_no=esu.esu_seri_no if isinstance(esu, ESU) else esu,
                firma_kodu=self._firma.firma_kodu,
                fatura=_fatura,
                lokasyon=lokasyon,
                mukellef=_mukellef,
                mulkiyet_sahibi=_mulkiyet_sahibi,
                sertifika=_sertifika,
            )
        elif isinstance(mukellef_bilgileri, ESUMukellefModel):
            veri = mukellef_bilgileri

        self.logger.debug(veri.json())

        return self._api_isteği(
            veri.dict(), istek_tipi=ESUServis._ISTEK_TIPI.ESU_MUKELLEF
        )

    def _esu_bilgisi_hazirla(self, kayit: dict) -> ESU:
        """
        Internal method to construct a charge point registration request model instance.

        Args:
            kayit (dict): Dictionary to convert to an ESU instance.

        Returns:
            ESU: Constructed charge point registration request model instance.
        """
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
        """Internal method to construct a tax payer registration request model instance.

        Args:
            kayit (dict): Dictionary to convert to an ESUMukellefModel instance
            esu (ESU): Charge point model instance

        Returns:
            ESUMukellefModel: Constructed tax payer registration request model instance.
        """
        lokasyon = Lokasyon(**kayit)
        if kayit.get("mukellef_vkn") and kayit.get("mukellef_unvan"):
            mukellef = Mukellef(**kayit)
        else:
            mukellef = Mukellef(
                mukellef_vkn=self._firma.firma_vkn,
                mukellef_unvan=str(self._firma.firma_unvan),
            )
        fatura = (
            Fatura(**kayit) if not kayit.get("mulkiyet_sahibi_vkn_tckn") else Fatura()
        )
        sertifika = Sertifika(**kayit) if kayit.get("sertifika_no") else Sertifika()
        mulkiyet = (
            MulkiyetSahibi(**kayit)
            if not kayit.get("fatura_ettn")
            else MulkiyetSahibi()
        )

        return ESUMukellefModel.olustur(
            esu_seri_no=esu.esu_seri_no,
            firma_kodu=self._firma.firma_kodu,
            fatura=fatura,
            lokasyon=lokasyon,
            mukellef=mukellef,
            mulkiyet_sahibi=mulkiyet,
            sertifika=sertifika,
        )

    def _kayit_isle(self, kayit: dict, sonuc: TopluKayitSonuc) -> None:
        """Internal method to register both the charge point and the tax payer.

        Args:
            kayit (dict): Dictionary corresponding to a row read from csv input
            sonuc (TopluKayitSonuc): Result model for processed registration requests
        """
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
        """Internal method to write the batch processing results to a file.

        Args:
            cikti_dosya_yolu (str): Output file path
            icerik (str): Data to write to the output file
        """
        with open(cikti_dosya_yolu, "w") as f:
            f.write(icerik)

    def toplu_kayit(
        self,
        giris_dosya_yolu: Optional[str] = None,  # using "envanter.csv" when None
        csv_string: Optional[io.StringIO] = None,
        dosyaya_yaz: Optional[bool] = None,
        cikti_dosya_yolu: Optional[
            str
        ] = None,  # using "gonderim_raporu.json" when None
        paralel_calistir: Optional[bool] = None,
        istekleri_logla: Optional[bool] = None,
    ) -> dict[str, Any]:
        """
        Batch registers charge points along with their tax payer information.

        Args:
            giris_dosya_yolu (Optional[str], optional):
                Input csv file path. Defaults to None.
            csv_string (Optional[io.StringIO], optional):
                String data stream as alternative input. Defaults to None.
            dosyaya_yaz (Optional[bool], optional):
                Boolean flag to control whether report the results to a file.
                Defaults to None.
            cikti_dosya_yolu (Optional[str], optional):
                Output file path (if `dosyaya_yaz` is True). Defaults to None.
            paralel (Optional[bool], optional):
                Boolean flag to control multithreaded processing. Defaults to None.
            istekleri_logla (Optional[bool], optional):
                Boolean flag to log api requests to console.

        Returns:
            dict[str, Any]: TopluKayitSonuc instance
            (which contains batch processing results) as a dictionary
        """
        working_dir = os.getcwd()
        csv_path = os.path.join(working_dir, "envanter.csv")

        if not giris_dosya_yolu and not csv_string and not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"{working_dir} dizininde envanter.csv dosyası bulunamadı"
            )

        if istekleri_logla:
            self.logger.setLevel(logging.DEBUG)

        records = PyUtils.read_csv(giris_dosya_yolu or csv_string or csv_path)
        self.logger.info(f"{giris_dosya_yolu or csv_path} giriş dosyası okundu")

        sonuc = TopluKayitSonuc(sonuclar=[], toplam=0)

        self.logger.info("GİB'e gönderim başlıyor...")

        if bool(paralel_calistir):

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max((os.cpu_count() or 6) - 2, 1)
            ) as executor:
                futures = [
                    executor.submit(self._kayit_isle, record, sonuc)
                    for record in records
                ]
                concurrent.futures.wait(
                    futures, return_when=concurrent.futures.ALL_COMPLETED
                )

        else:
            for record in records:
                self._kayit_isle(record, sonuc)

        sonuc.toplam = len(sonuc.sonuclar)

        if bool(dosyaya_yaz):
            self._dosyaya_yaz(
                cikti_dosya_yolu=(cikti_dosya_yolu or "gonderim_raporu.json"),
                icerik=sonuc.json(indent=4),
            )

        # conditionally restore default logging level
        if istekleri_logla:
            self.logger.setLevel(logging.INFO)

        return sonuc.dict()

    def kayit_guncelle(
        self,
        kayit_bilgileri: Union[ESUGuncellemeModel, Any] = None,
        esu_seri_no: Optional[str] = None,
        lokasyon: Optional[Lokasyon] = None,
        fatura: Optional[Fatura] = None,
        mulkiyet_sahibi: Optional[MulkiyetSahibi] = None,
        sertifika: Optional[Sertifika] = None,
    ) -> Yanit:
        """Updates a previously registered charge point's information.

        Args:
            kayit_bilgileri (Union[ESUGuncellemeModel, Any], optional):
                Charge point update request model. Defaults to None.
            esu_seri_no (Optional[str], optional):
                Charge point serial number. Defaults to None.
            lokasyon (Optional[Lokasyon], optional):
                Location information. Defaults to None.
            fatura (Optional[Fatura], optional):
                Invoice information. Defaults to None.
            mulkiyet_sahibi (Optional[MulkiyetSahibi], optional):
                Ownership information. Defaults to None.
            sertifika (Optional[Sertifika], optional):
                Certificate information. Defaults to None.

        Raises:
            ValueError: When some information is missing to construct the request model

        Returns:
            Yanit: GIB ESU EKS service reponse
        """
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

        self.logger.debug(veri.json())

        return self._api_isteği(
            veri.dict(), istek_tipi=ESUServis._ISTEK_TIPI.ESU_GUNCELLEME
        )

    def _guncelleme_kaydi_isle(self, kayit: dict, sonuc: TopluGuncellemeSonuc) -> None:
        """Internal method to update a previously registered charge point's information.

        Args:
            kayit (dict): Dictionary corresponding to a row read from csv input
            sonuc (TopluGuncellemeSonuc): Result model for processed update requests
        """

        guncelleme_yanit = self.kayit_guncelle(
            esu_seri_no=kayit["esu_seri_no"],
            lokasyon=Lokasyon(**kayit),
            fatura=(
                Fatura(**kayit)
                if not kayit.get("mulkiyet_sahibi_vkn_tckn")
                else Fatura()
            ),
            sertifika=Sertifika(**kayit) if kayit.get("sertifika_no") else Sertifika(),
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
        giris_dosya_yolu: Optional[str] = None,  # using "envanter.csv" when None
        csv_string: Optional[io.StringIO] = None,
        dosyaya_yaz: Optional[bool] = None,
        cikti_dosya_yolu: Optional[
            str
        ] = None,  # using "gonderim_raporu.json" when None
        paralel_calistir: Optional[bool] = None,
        istekleri_logla: Optional[bool] = None,
    ) -> dict[str, Any]:
        """
        Batch updates previously registered charge points' information.

        Args:
            giris_dosya_yolu (Optional[str], optional):
                Input csv file path. Defaults to None.
            csv_string (Optional[io.StringIO], optional):
                String data stream as alternative input. Defaults to None.
            dosyaya_yaz (Optional[bool], optional):
                Boolean flag to control whether report the results to a file.
                Defaults to None.
            cikti_dosya_yolu (Optional[str], optional):
                Output file path (if `dosyaya_yaz` is True). Defaults to None.
            paralel (Optional[bool], optional):
                Boolean flag to control multithreaded processing. Defaults to None.
            istekleri_logla (Optional[bool], optional):
                Boolean flag to log api requests to console.

        Returns:
            dict[str, Any]: TopluGuncellemeSonuc instance
            (which contains batch update results) as a dictionary
        """

        working_dir = os.getcwd()
        csv_path = os.path.join(working_dir, "envanter.csv")

        if not giris_dosya_yolu and not csv_string and not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"{working_dir} dizininde envanter.csv dosyası bulunamadı"
            )

        if istekleri_logla:
            self.logger.setLevel(logging.DEBUG)

        records = PyUtils.read_csv(giris_dosya_yolu or csv_string or csv_path)
        self.logger.info(f"{giris_dosya_yolu or csv_path} giriş dosyası okundu")

        sonuc = TopluGuncellemeSonuc(sonuclar=[], toplam=0)

        self.logger.info("GİB'e gönderim başlıyor...")

        if bool(paralel_calistir):

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max((os.cpu_count() or 6) - 2, 1)
            ) as executor:
                futures = [
                    executor.submit(self._guncelleme_kaydi_isle, record, sonuc)
                    for record in records
                ]
                concurrent.futures.wait(
                    futures, return_when=concurrent.futures.ALL_COMPLETED
                )

        else:
            for record in records:
                self._guncelleme_kaydi_isle(record, sonuc)

        sonuc.toplam = len(sonuc.sonuclar)

        if bool(dosyaya_yaz):
            self._dosyaya_yaz(
                cikti_dosya_yolu=(cikti_dosya_yolu or "gonderim_raporu.json"),
                icerik=sonuc.json(),
            )

        # conditionally restore default logging level
        if istekleri_logla:
            self.logger.setLevel(logging.INFO)

        return sonuc.dict()

    def cihaz_kapatma(
        self,
        cihaz_bilgisi: Optional[ESUKapatmaModel] = None,
        esu_seri_no: Optional[str] = None,
    ) -> Yanit:
        """Unregisters/delists a previously registered charge point.

        Args:
            cihaz_bilgisi (Optional[ESUKapatmaModel], optional):
                Charge point delisting request model. Defaults to None.
            esu_seri_no (Optional[str], optional):
                Charge point serial number. Defaults to None.

        Raises:
            ValueError: When none of the arguments are provided

        Returns:
            Yanit: GIB ESU EKS service reponse
        """

        cihaz = (
            cihaz_bilgisi
            if cihaz_bilgisi and isinstance(cihaz_bilgisi, ESUKapatmaModel)
            else (
                ESUKapatmaModel(
                    firma_kodu=self._firma.firma_kodu,
                    kapatma_bilgisi=ESUSeriNo(esu_seri_no=esu_seri_no),
                )
                if esu_seri_no
                else None
            )
        )
        if cihaz is None:
            raise ValueError(
                "`cihaz_bilgisi` ya da `esu_seri_no` "
                "verilmemiş ya da verili değer geçersiz"
            )
        return self._api_isteği(
            cihaz.dict(), istek_tipi=ESUServis._ISTEK_TIPI.ESU_KAPATMA
        )
