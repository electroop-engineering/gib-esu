# regex patterns

from enum import Enum
from typing import Annotated, List

from pydantic import Field, PositiveInt

from gib_esu.models.base_model import CustomBaseModel
from gib_esu.models.request_models import NonEmptyString

RegEx__Api_Durum_Kodu = r"^\b\d{4}\b$"

# enums


class Durum(str, Enum):
    """Enum for API response status codes."""

    SUCCESS = "success"
    FAILURE = "basarisiz"


# api response model


class Sonuc(CustomBaseModel):
    """Api result model."""

    esu_seri_no: NonEmptyString
    sira_no: PositiveInt
    kod: str = Field(pattern=RegEx__Api_Durum_Kodu)
    mesaj: str


class Yanit(CustomBaseModel):
    """Api response model."""

    durum: Durum
    sonuc: Annotated[List[Sonuc], Field(default_factory=list, min_length=1)]
