import csv
import io
from typing import Dict, List, Union


class PyUtils:
    """Class encapsulating various python utility methods."""

    @classmethod
    def read_csv(
        cls, filepath_or_buffer: Union[str, io.StringIO]
    ) -> List[Dict[str, str]]:
        """Reads input data from a CSV file or string stream.

        Args:
            filepath_or_buffer (Union[str, io.StringIO]): Path to a CSV file
            or a string stream containing CSV data.

        Returns:
            List[Dict[str, str]]: A list of dictionaries representing rows in the CSV
            with all fields as strings.
        """

        if isinstance(filepath_or_buffer, str) and not isinstance(
            filepath_or_buffer, io.StringIO
        ):
            file = open(filepath_or_buffer, mode="r", encoding="utf-8")
        else:
            file = filepath_or_buffer

        with file:
            reader = csv.DictReader(file)

            records = []
            for row in reader:
                record = {
                    key: str(row.get(key, "") or "") for key in reader.fieldnames or []
                }
                records.append(record)

        return records
