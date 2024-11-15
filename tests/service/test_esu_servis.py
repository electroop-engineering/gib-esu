import io
import json
from io import StringIO
from typing import Any
from unittest.mock import mock_open, patch

import pytest
import requests_mock
from dotenv import dotenv_values

from models.esu_kayit import ESU, ESUSoketTipi, Soket, SoketTipi
from models.esu_mukellef import (
    ESUMukellef,
    ESUMukellefBilgisi,
    ESUMukellefModel,
    Fatura,
    Lokasyon,
    Mukellef,
)
from models.servis_modelleri import (
    Durum,
    ESUTopluKayitSonucu,
    Sonuc,
    TopluKayitSonuc,
    Yanit,
)
from service.esu_service import ESUServis


@pytest.fixture
def test_config() -> str:
    return (
        "PROD_API=0\nSSL_DOGRULAMA=0\nTEST_FIRMA_KULLAN=0\n"
        "GIB_FIRMA_KODU=J000\nGIB_API_SIFRE=123456\n"
        "FIRMA_UNVAN=ENERJİ ANONİM ŞİRKETİ\n"
        "FIRMA_VKN=1234567890\n"
        "EPDK_LISANS_KODU=ŞH/12345-6/00789\n"
        "GIB_API_URL=https://okctest.gib.gov.tr/api/v1/\n"
        "GIB_TEST_FIRMA_VKN=3900383669"
    )


@pytest.fixture
def test_esu() -> ESU:
    return ESU(
        esu_seri_no="123",
        esu_markasi="ABB",
        esu_modeli="DC-Model",
        esu_soket_tipi=ESUSoketTipi.AC_DC,
        esu_soket_sayisi="2",
        esu_soket_detay=[
            Soket(soket_no="Soket1", soket_tip=SoketTipi.AC),
            Soket(soket_no="Soket2", soket_tip=SoketTipi.DC),
        ],
    )


@pytest.fixture
def test_lokasyon() -> Lokasyon:
    return Lokasyon(il_kodu="034", ilce="Beşiktaş", adres_numarası="", koordinat="")


@pytest.fixture
def test_fatura() -> Fatura:
    return Fatura(fatura_ettn="ff01-345-445", fatura_tarihi="2024-12-19")


@pytest.fixture
def test_mukellef() -> Mukellef:
    return Mukellef(mukellef_vkn="1234567890", mukellef_unvan="ABC A.Ş.")


@pytest.fixture
def test_yanit() -> Yanit:
    return Yanit(
        durum=Durum.SUCCESS,
        sonuc=[
            Sonuc(
                esu_seri_no="123",
                sira_no=1,
                kod="1000",
                mesaj="Basarili",
            )
        ],
    )


@pytest.fixture
def test_kayit_sonuc() -> TopluKayitSonuc:
    return TopluKayitSonuc(
        sonuclar=[
            ESUTopluKayitSonucu(
                mukellef_kayit_sonucu="Basarili",
                esu_kayit_sonucu="Basarili",
                esu_seri_no="123",
            ),
        ],
        toplam=1,
    )


@pytest.fixture
def mock_api() -> Any:
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def sample_csv() -> io.StringIO:
    csv_content = (
        "esu_seri_no,esu_soket_tipi,esu_soket_sayisi,esu_soket_detay,"
        "esu_markasi,esu_modeli,il_kodu,ilce,fatura_tarihi,fatura_ettn,"
        "mukellef_vkn,mukellef_unvan,sertifika_no,sertifika_tarihi,"
        "mulkiyet_vkn,mulkiyet_unvan\n123,AC,1,Soket1:AC,"
        "Vestel,EVC04,034,Üsküdar,2024-08-29,P012024053447,,,,,,"
    )
    return io.StringIO(csv_content)


@pytest.fixture
def sample_csv2() -> io.StringIO:
    csv_content = (
        "esu_seri_no,esu_soket_tipi,esu_soket_sayisi,esu_soket_detay,"
        "esu_markasi,esu_modeli,il_kodu,ilce,fatura_tarihi,fatura_ettn,"
        "mukellef_vkn,mukellef_unvan,sertifika_no,sertifika_tarihi,"
        "mulkiyet_vkn,mulkiyet_unvan\n123,AC,1,Soket1:AC,"
        "Vestel,EVC04,034,Üsküdar,2024-08-19,P012024053446,,,,,,"
    )
    return io.StringIO(csv_content)


@pytest.fixture
def sample_csv3() -> io.StringIO:
    csv_content = (
        "esu_seri_no,esu_soket_tipi,esu_soket_sayisi,esu_soket_detay,"
        "esu_markasi,esu_modeli,il_kodu,ilce,fatura_tarihi,fatura_ettn,"
        "mukellef_vkn,mukellef_unvan,sertifika_no,sertifika_tarihi,"
        "mulkiyet_vkn,mulkiyet_unvan\n123,AC,1,Soket1:AC,"
        "Vestel,EVC04,034,Üsküdar,2024-01-16,P012024153446,,,,,,"
    )
    return io.StringIO(csv_content)


def test_esu_servis_instantiation(test_config: str) -> None:
    """Test ESUServis instantiation."""

    try:
        ESUServis(_config=dotenv_values(stream=StringIO(test_config)))
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")


def test_esu_servis_cihaz_kayit(
    test_config: str, test_esu: ESU, test_yanit: Yanit, mock_api: Any
) -> None:
    """Test cihaz_kayit method."""

    servis = ESUServis(_config=dotenv_values(stream=StringIO(test_config)))

    mock_api.post(
        f"{servis._api.api_url}{ESUServis.ISTEK_TIPI.ESU_KAYIT}",
        json=test_yanit.model_dump(),
    )

    resp: Yanit = servis.cihaz_kayit(test_esu)
    assert resp.sonuc[0].esu_seri_no == test_esu.esu_seri_no


def test_mukellef_kayit(
    test_config: str,
    test_esu: ESU,
    test_lokasyon: Lokasyon,
    test_mukellef: Mukellef,
    test_fatura: Fatura,
    test_yanit: Yanit,
    mock_api: Any,
) -> None:
    """Test mukellef_kayit method."""

    servis = ESUServis(_config=dotenv_values(stream=StringIO(test_config)))

    mock_api.post(
        f"{servis._api.api_url}{ESUServis.ISTEK_TIPI.ESU_MUKELLEF}",
        json=test_yanit.model_dump(),
    )

    resp = servis.mukellef_kayit(
        esu=test_esu,
        lokasyon=test_lokasyon,
        mukellef=test_mukellef,
        fatura=test_fatura,
    )
    assert resp.sonuc[0].esu_seri_no == test_esu.esu_seri_no

    resp = servis.mukellef_kayit(
        mukellef_bilgileri=ESUMukellef(
            model=ESUMukellefModel(
                firma_kodu=servis._firma.firma_kodu,
                durum_bilgileri=ESUMukellefBilgisi(
                    esu_seri_no=test_esu.esu_seri_no,
                    fatura_ettn=test_fatura.fatura_ettn,
                    fatura_tarihi=test_fatura.fatura_tarihi,
                    mukellef_vkn=test_mukellef.mukellef_vkn,
                    mukellef_unvan=test_mukellef.mukellef_unvan,
                    il_kodu=test_lokasyon.il_kodu,
                    ilce=test_lokasyon.ilce,
                    adres_numarası=test_lokasyon.adres_numarası,
                    koordinat=test_lokasyon.koordinat,
                    sertifika_no="",
                    sertifika_tarihi="",
                    mulkiyet_sahibi_vkn_tckn="",
                    mulkiyet_sahibi_ad_unvan="",
                ),
            )
        )
    )
    assert resp.sonuc[0].esu_seri_no == test_esu.esu_seri_no

    with pytest.raises(ValueError) as e:
        resp = servis.mukellef_kayit(
            esu=test_esu,
            lokasyon=test_lokasyon,
            # mukellef missing mukellef=test_mukellef,
            fatura=test_fatura,
        )
    assert e.value.args[0] == "Mükellef bilgileri eksik"


def test_toplu_kayit(
    sample_csv: io.StringIO,
    sample_csv2: io.StringIO,
    sample_csv3: io.StringIO,
    test_config: str,
    test_esu: ESU,
    test_kayit_sonuc: TopluKayitSonuc,
    test_yanit: Yanit,
    mock_api: Any,
) -> None:
    """Test toplu_kayit method."""

    servis = ESUServis(_config=dotenv_values(stream=StringIO(test_config)))

    mock_api.post(
        f"{servis._api.api_url}{ESUServis.ISTEK_TIPI.ESU_KAYIT}",
        json=test_yanit.model_dump(),
    )
    mock_api.post(
        f"{servis._api.api_url}{ESUServis.ISTEK_TIPI.ESU_MUKELLEF}",
        json=test_yanit.model_dump(),
    )

    resp = servis.toplu_kayit(csv_string=sample_csv)

    assert TopluKayitSonuc(**resp).sonuclar[0].esu_seri_no == test_esu.esu_seri_no
    assert (
        TopluKayitSonuc(**resp).sonuclar[0].esu_seri_no
        == test_yanit.sonuc[0].esu_seri_no
    )

    resp = servis.toplu_kayit(csv_string=sample_csv2, paralel=True)
    assert TopluKayitSonuc(**resp).sonuclar[0].esu_seri_no == test_esu.esu_seri_no
    assert (
        TopluKayitSonuc(**resp).sonuclar[0].esu_seri_no
        == test_yanit.sonuc[0].esu_seri_no
    )

    dummy_output_path = "mocked_file.json"

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        # Call the real _dosyaya_yaz method
        servis._dosyaya_yaz(dummy_output_path, "mocked_content")

    mock_file.assert_called_once_with(dummy_output_path, "w")
    mock_file().write.assert_called_once_with("mocked_content")

    with patch("service.esu_service.ESUServis._dosyaya_yaz") as mock_write:
        resp = servis.toplu_kayit(
            csv_string=sample_csv3, dosyaya_yaz=True, cikti_dosya_yolu=dummy_output_path
        )
        mock_write.assert_called_once_with(
            cikti_dosya_yolu=dummy_output_path,
            icerik=json.dumps(test_kayit_sonuc.model_dump(), indent=4),
        )
