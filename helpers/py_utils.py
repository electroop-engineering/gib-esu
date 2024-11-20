import io
from typing import Union

import pandas as pd
from pandas import DataFrame
from pydantic import FilePath


class PyUtils:
    """Class encapsulating various python utility methods."""

    @classmethod
    def read_csv_input(
        cls, filepath_or_buffer: Union[FilePath, str, io.StringIO]
    ) -> DataFrame:
        """Reads input data either from a csv formatted text file or string stream.

        Args:
            filepath_or_buffer (Union[FilePath, str, io.StringIO]):
            Csv input file path or string input stream to extract the data from

        Returns:
            DataFrame: A pandas DataFrame corresponding to csv data
        """

        # names of columns whose data should be interpreted as string type
        column_names = ["il_kodu", "esu_seri_no", "esu_soket_sayisi", "mukellef_vkn"]

        records = pd.read_csv(
            filepath_or_buffer,
            dtype={
                column_names[0]: str,
                column_names[1]: str,
                column_names[2]: str,
                column_names[3]: str,
            },
        )

        # replace NA/NaN values with empty strings
        records = records.fillna("")
        return records
