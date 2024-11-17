import io

import pytest

from helpers.py_utils import PyUtils
from models.sabitler import (
    F_ESU_SERI_NO,
    F_FATURA_ETTN,
    F_FATURA_TARIHI,
    F_IL_KODU,
    F_ILCE,
    F_MARKA,
    F_MODEL,
    F_MUKELLEF_UNVAN,
    F_MUKELLEF_VKN,
    F_SAHIP_AD_UNVAN,
    F_SAHIP_VKN_TCKN,
    F_SERTIFIKA_NO,
    F_SERTIFIKA_TARIHI,
    F_SOKET_DETAY,
    F_SOKET_SAYISI,
    F_SOKET_TIPI,
    STR_BOS,
)


@pytest.fixture
def sample_csv() -> io.StringIO:
    csv_content = (
        "esu_seri_no,esu_soket_tipi,esu_soket_sayisi,esu_soket_detay,"
        "esu_markasi,esu_modeli,il_kodu,ilce,fatura_tarihi,fatura_ettn,"
        "mukellef_vkn,mukellef_unvan,sertifika_no,sertifika_tarihi,"
        "mulkiyet_sahibi_vkn_tckn,mulkiyet_sahibi_ad_unvan\n700113,AC,1,Soket1:AC,"
        'Vestel,EVC04,"034",Üsküdar,2024-08-29,P012024053447,,,,,,'
    )
    return io.StringIO(csv_content)


def test_read_csv(sample_csv: io.StringIO) -> None:
    """Test PyUtils.read_csv method."""

    df = PyUtils.read_csv_input(sample_csv)

    assert df.shape == (1, 16)  # 1 row, 16 columns
    assert df.loc[0, F_ESU_SERI_NO] == "700113"
    assert df.loc[0, F_SOKET_TIPI] == "AC"
    assert df.loc[0, F_SOKET_SAYISI] == "1"
    assert df.loc[0, F_SOKET_DETAY] == "Soket1:AC"
    assert df.loc[0, F_MARKA] == "Vestel"
    assert df.loc[0, F_MODEL] == "EVC04"
    assert df.loc[0, F_IL_KODU] == "034"
    assert df.loc[0, F_ILCE] == "Üsküdar"
    assert df.loc[0, F_FATURA_TARIHI] == "2024-08-29"
    assert df.loc[0, F_FATURA_ETTN] == "P012024053447"
    assert df.loc[0, F_MUKELLEF_VKN] == STR_BOS
    assert df.loc[0, F_MUKELLEF_UNVAN] == STR_BOS
    assert df.loc[0, F_SERTIFIKA_NO] == STR_BOS
    assert df.loc[0, F_SERTIFIKA_TARIHI] == STR_BOS
    assert df.loc[0, F_SAHIP_VKN_TCKN] == STR_BOS
    assert df.loc[0, F_SAHIP_AD_UNVAN] == STR_BOS


def test_pad_with_zeroes() -> None:
    """Test PyUtils.pad_with_zeroes method."""

    padded = PyUtils.pad_with_zeroes("123456789")
    assert len(padded) == 10 and padded == "0123456789"

    padded = PyUtils.pad_with_zeroes("12345678901")
    assert len(padded) == 11 and padded == "12345678901"

    padded = PyUtils.pad_with_zeroes("912345")
    assert len(padded) == 10 and padded == "0000912345"
