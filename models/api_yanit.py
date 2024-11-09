from enum import Enum
from typing import List

from pydantic import BaseModel, Field, PositiveInt


class Durum(str, Enum):
    SUCCESS = "success"
    FAILURE = "basarisiz"


class Sonuc(BaseModel):
    esu_seri_no: str = Field(min_length=3)
    sira_no: PositiveInt
    kod: str = Field(pattern=r"^\"d{4}\"$")
    mesaj: str


class Yanit(BaseModel):
    durum: Durum
    sonuc: List[Sonuc]
