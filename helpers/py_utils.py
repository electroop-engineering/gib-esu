import io
from typing import Any, Union

import pandas as pd
from pandas import DataFrame
from pydantic import FilePath

from models.constants import F_ESU_SERI_NO, F_IL_KODU, F_SOKET_SAYISI, LEN_VKN, STR_BOS


class PyUtils:
    @classmethod
    def read_csv_input(
        cls, filepath_or_buffer: Union[FilePath, str, io.StringIO]
    ) -> DataFrame:
        column_names = [F_IL_KODU, F_ESU_SERI_NO, F_SOKET_SAYISI]
        records = pd.read_csv(
            filepath_or_buffer,
            dtype={
                column_names[0]: str,
                column_names[1]: str,
                column_names[2]: str,
            },
        )
        records = records.fillna(STR_BOS)
        return records

    @classmethod
    def pad_with_zeroes(cls, digits: Any) -> str:
        digits_str = str(int(digits))
        padded_str = digits_str.zfill(LEN_VKN)
        return padded_str
