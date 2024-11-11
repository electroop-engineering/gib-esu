import io
from typing import Any, Union

import pandas as pd
from pandas import DataFrame
from pydantic import FilePath


class PyUtils:
    @classmethod
    def read_csv_input(
        cls, filepath_or_buffer: Union[FilePath, str, io.StringIO]
    ) -> DataFrame:
        column_names = ["il_kodu", "esu_seri_no", "esu_soket_sayisi"]
        records = pd.read_csv(
            filepath_or_buffer,
            dtype={
                column_names[0]: str,
                column_names[1]: str,
                column_names[2]: str,
            },
        )
        records = records.fillna("")
        return records

    @classmethod
    def pad_with_zeroes(cls, digits: Any) -> str:
        digits_str = str(int(digits))
        padded_str = digits_str.zfill(10)
        return padded_str
