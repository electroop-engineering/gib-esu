import io
from typing import Union
from unittest.mock import mock_open, patch

import pytest

from gib_esu.helpers import PyUtils


def make_csv(stream: bool = True) -> Union[io.StringIO, str]:
    csv_content = (
        "esu_seri_no,esu_soket_tipi,esu_soket_sayisi,esu_soket_detay,"
        "esu_markasi,esu_modeli,il_kodu,ilce,fatura_tarihi,fatura_ettn,"
        "mukellef_vkn,mukellef_unvan,sertifika_no,sertifika_tarihi,"
        "mulkiyet_sahibi_vkn_tckn,mulkiyet_sahibi_ad_unvan\n700113,AC,1,Soket1:AC,"
        'Vestel,EVC04,"034",Üsküdar,2024-08-29,P012024053447,,,,,,'
    )
    return io.StringIO(csv_content) if stream else csv_content


@pytest.mark.parametrize("csv", [make_csv(), make_csv(False)])
def test_read_csv(csv: Union[io.StringIO, str]) -> None:
    """Test PyUtils.read_csv method."""

    if isinstance(csv, io.StringIO):
        rows = PyUtils.read_csv(csv)
    else:
        mock_file_content = csv
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            rows = PyUtils.read_csv("mocked_file.csv")

    assert len(rows) == 1
    assert len(rows[0].keys()) == 16
    assert rows[0].get("esu_seri_no") == "700113"
    assert rows[0].get("esu_soket_tipi") == "AC"
    assert rows[0].get("esu_soket_sayisi") == "1"
    assert rows[0].get("esu_soket_detay") == "Soket1:AC"
    assert rows[0].get("esu_markasi") == "Vestel"
    assert rows[0].get("esu_modeli") == "EVC04"
    assert rows[0].get("il_kodu") == "034"
    assert rows[0].get("ilce") == "Üsküdar"
    assert rows[0].get("fatura_tarihi") == "2024-08-29"
    assert rows[0].get("fatura_ettn") == "P012024053447"
    assert rows[0].get("mukellef_vkn") == ""
    assert rows[0].get("mukellef_unvan") == ""
    assert rows[0].get("sertifika_no") == ""
    assert rows[0].get("sertifika_tarihi") == ""
    assert rows[0].get("mulkiyet_sahibi_vkn_tckn") == ""
    assert rows[0].get("mulkiyet_sahibi_ad_unvan") == ""
