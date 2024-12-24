# regex patterns

from enum import Enum
from typing import List

from gib_esu.models.base_model import CustomBaseModel
from pydantic import Field, PositiveInt, constr

RegEx__Api_Durum_Kodu = r"^\b\d{4}\b$"

# enums


class Durum(str, Enum):
    """Enum for API response status codes."""

    SUCCESS = "success"
    FAILURE = "basarisiz"


# api response model


class Sonuc(CustomBaseModel):
    """Api result model."""

    esu_seri_no: constr(strip_whitespace=True, min_length=1)  # type: ignore
    sira_no: PositiveInt
    kod: constr(regex=RegEx__Api_Durum_Kodu)  # type: ignore
    mesaj: str


class Yanit(CustomBaseModel):
    """Api response model."""

    durum: Durum
    sonuc: List[Sonuc] = Field(default_factory=list, min_items=1)
