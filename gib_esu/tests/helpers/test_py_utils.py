import io

import pytest

from gib_esu.helpers.py_utils import PyUtils


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
    assert df.loc[0, "esu_seri_no"] == "700113"
    assert df.loc[0, "esu_soket_tipi"] == "AC"
    assert df.loc[0, "esu_soket_sayisi"] == "1"
    assert df.loc[0, "esu_soket_detay"] == "Soket1:AC"
    assert df.loc[0, "esu_markasi"] == "Vestel"
    assert df.loc[0, "esu_modeli"] == "EVC04"
    assert df.loc[0, "il_kodu"] == "034"
    assert df.loc[0, "ilce"] == "Üsküdar"
    assert df.loc[0, "fatura_tarihi"] == "2024-08-29"
    assert df.loc[0, "fatura_ettn"] == "P012024053447"
    assert df.loc[0, "mukellef_vkn"] == ""
    assert df.loc[0, "mukellef_unvan"] == ""
    assert df.loc[0, "sertifika_no"] == ""
    assert df.loc[0, "sertifika_tarihi"] == ""
    assert df.loc[0, "mulkiyet_sahibi_vkn_tckn"] == ""
    assert df.loc[0, "mulkiyet_sahibi_ad_unvan"] == ""
